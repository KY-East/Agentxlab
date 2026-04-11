"""Subscription management + payment endpoints (Stripe & Crypto)."""

from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime, timedelta, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.subscription import Subscription, PaymentRecord
from app.models.user import User
from app.plan_config import PLAN_CONFIG, get_plan
from app.services.auth import get_current_user, get_verified_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["subscription"])

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


# ── Helpers ────────────────────────────────────────────────────────

def get_or_create_subscription(user_id: int, db: Session) -> Subscription:
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if sub:
        return sub
    plan = get_plan("free")
    sub = Subscription(
        user_id=user_id,
        plan="free",
        status="active",
        monthly_token_limit=plan["monthly_tokens"],
        tokens_used_this_month=0,
        allowed_models=json.dumps(plan["allowed_models"]),
        preferred_model=plan["allowed_models"][0],
        quota_reset_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def activate_plan(sub: Subscription, plan_name: str, db: Session) -> None:
    plan = get_plan(plan_name)
    sub.plan = plan_name
    sub.status = "active"
    sub.monthly_token_limit = plan["monthly_tokens"]
    sub.tokens_used_this_month = 0
    sub.allowed_models = json.dumps(plan["allowed_models"])
    if sub.preferred_model not in plan["allowed_models"]:
        sub.preferred_model = plan["allowed_models"][0]
    sub.quota_reset_at = datetime.now(timezone.utc) + timedelta(days=30)
    db.commit()


# ── Schemas ────────────────────────────────────────────────────────

class SubscriptionOut(BaseModel):
    plan: str
    status: str
    monthly_token_limit: int
    tokens_used_this_month: int
    quota_reset_at: datetime | str | None = None
    allowed_models: list[str] = []
    preferred_model: str | None = None
    stripe_customer_id: str | None = None

    model_config = {"from_attributes": True}


class PlanOut(BaseModel):
    name: str
    label_en: str
    label_zh: str
    monthly_tokens: int
    allowed_models: list[str]
    price_monthly_cents: int
    price_once_cents: int


class ModelUpdateReq(BaseModel):
    preferred_model: str


class CryptoRequestBody(BaseModel):
    plan: str
    tx_hash: str | None = None


class CryptoConfirmBody(BaseModel):
    payment_record_id: int


# ── Subscription Endpoints ─────────────────────────────────────────

@router.get("/api/subscription/plans", response_model=list[PlanOut])
def list_plans():
    result = []
    for name, cfg in PLAN_CONFIG.items():
        result.append(PlanOut(
            name=name,
            label_en=cfg["label_en"],
            label_zh=cfg["label_zh"],
            monthly_tokens=cfg["monthly_tokens"],
            allowed_models=cfg["allowed_models"],
            price_monthly_cents=cfg.get("price_monthly_cents", 0),
            price_once_cents=cfg.get("price_once_cents", 0),
        ))
    return result


@router.get("/api/subscription/me", response_model=SubscriptionOut)
def get_my_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = get_or_create_subscription(user.id, db)
    models = []
    if sub.allowed_models:
        try:
            models = json.loads(sub.allowed_models)
        except (json.JSONDecodeError, TypeError):
            models = []
    return SubscriptionOut(
        plan=sub.plan,
        status=sub.status,
        monthly_token_limit=sub.monthly_token_limit,
        tokens_used_this_month=sub.tokens_used_this_month,
        quota_reset_at=sub.quota_reset_at,
        allowed_models=models,
        preferred_model=sub.preferred_model,
        stripe_customer_id=sub.stripe_customer_id,
    )


@router.patch("/api/subscription/model", response_model=SubscriptionOut)
def update_preferred_model(
    body: ModelUpdateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = get_or_create_subscription(user.id, db)
    allowed = []
    if sub.allowed_models:
        try:
            allowed = json.loads(sub.allowed_models)
        except (json.JSONDecodeError, TypeError):
            allowed = []
    if body.preferred_model not in allowed:
        raise HTTPException(403, f"Model '{body.preferred_model}' is not available on your plan")
    sub.preferred_model = body.preferred_model
    db.commit()
    db.refresh(sub)
    return get_my_subscription.__wrapped__(user=user, db=db) if False else SubscriptionOut(
        plan=sub.plan,
        status=sub.status,
        monthly_token_limit=sub.monthly_token_limit,
        tokens_used_this_month=sub.tokens_used_this_month,
        quota_reset_at=sub.quota_reset_at,
        allowed_models=allowed,
        preferred_model=sub.preferred_model,
        stripe_customer_id=sub.stripe_customer_id,
    )


@router.get("/api/subscription/usage")
def get_usage(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = get_or_create_subscription(user.id, db)
    records = (
        db.query(PaymentRecord)
        .filter(PaymentRecord.user_id == user.id)
        .order_by(PaymentRecord.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "tokens_used": sub.tokens_used_this_month,
        "tokens_limit": sub.monthly_token_limit,
        "quota_reset_at": sub.quota_reset_at,
        "payments": [
            {
                "id": r.id,
                "amount_cents": r.amount_cents,
                "currency": r.currency,
                "payment_method": r.payment_method,
                "plan": r.plan,
                "status": r.status,
                "created_at": r.created_at,
            }
            for r in records
        ],
    }


# ── Stripe Endpoints ──────────────────────────────────────────────

@router.post("/api/payment/stripe/checkout")
def create_checkout_session(
    plan: str,
    user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    if not settings.stripe_secret_key:
        raise HTTPException(501, "Stripe is not configured")
    if plan not in ("pro", "lifetime"):
        raise HTTPException(400, "Invalid plan. Choose 'pro' or 'lifetime'.")

    sub = get_or_create_subscription(user.id, db)

    if not sub.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": str(user.id)})
        sub.stripe_customer_id = customer.id
        db.commit()

    price_id = settings.stripe_pro_price_id if plan == "pro" else settings.stripe_lifetime_price_id
    if not price_id:
        raise HTTPException(501, f"Stripe price for '{plan}' is not configured")

    mode = "subscription" if plan == "pro" else "payment"
    session = stripe.checkout.Session.create(
        customer=sub.stripe_customer_id,
        mode=mode,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.app_base_url}/profile?payment=success",
        cancel_url=f"{settings.app_base_url}/profile?payment=cancelled",
        metadata={"user_id": str(user.id), "plan": plan},
    )
    return {"checkout_url": session.url}


@router.post("/api/payment/stripe/portal")
def create_portal_session(
    user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    if not settings.stripe_secret_key:
        raise HTTPException(501, "Stripe is not configured")
    sub = get_or_create_subscription(user.id, db)
    if not sub.stripe_customer_id:
        raise HTTPException(400, "No billing account found")
    session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=f"{settings.app_base_url}/profile",
    )
    return {"portal_url": session.url}


@router.post("/api/payment/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if settings.stripe_webhook_secret:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
        except (stripe.error.SignatureVerificationError, ValueError) as e:
            logger.warning("Stripe webhook signature failed: %s", e)
            raise HTTPException(400, "Invalid signature")
    else:
        import json as _json
        event = _json.loads(payload)

    event_type = event.get("type", "") if isinstance(event, dict) else event.type
    data_obj = event.get("data", {}).get("object", {}) if isinstance(event, dict) else event.data.object

    logger.info("Stripe webhook: %s", event_type)

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(data_obj, db)
    elif event_type == "invoice.paid":
        _handle_invoice_paid(data_obj, db)
    elif event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        _handle_subscription_change(data_obj, db)

    return {"ok": True}


def _handle_checkout_completed(session_data: dict, db: Session) -> None:
    metadata = session_data.get("metadata", {})
    user_id = metadata.get("user_id")
    plan = metadata.get("plan")
    if not user_id or not plan:
        return

    user_id = int(user_id)
    sub = get_or_create_subscription(user_id, db)

    amount = session_data.get("amount_total", 0)
    db.add(PaymentRecord(
        user_id=user_id,
        amount_cents=amount,
        currency="usd",
        payment_method="stripe",
        payment_ref=session_data.get("payment_intent") or session_data.get("subscription") or session_data.get("id"),
        plan=plan,
        status="succeeded",
    ))

    if plan == "pro":
        sub.stripe_subscription_id = session_data.get("subscription")
    activate_plan(sub, plan, db)
    db.commit()


def _handle_invoice_paid(invoice_data: dict, db: Session) -> None:
    customer_id = invoice_data.get("customer")
    if not customer_id:
        return
    sub = db.query(Subscription).filter(Subscription.stripe_customer_id == customer_id).first()
    if not sub:
        return
    sub.tokens_used_this_month = 0
    sub.quota_reset_at = datetime.now(timezone.utc) + timedelta(days=30)
    sub.status = "active"
    db.commit()


def _handle_subscription_change(sub_data: dict, db: Session) -> None:
    customer_id = sub_data.get("customer")
    status = sub_data.get("status")
    if not customer_id:
        return
    sub = db.query(Subscription).filter(Subscription.stripe_customer_id == customer_id).first()
    if not sub:
        return
    if status in ("canceled", "unpaid"):
        activate_plan(sub, "free", db)
        sub.stripe_subscription_id = None
        db.commit()
    elif status == "past_due":
        sub.status = "past_due"
        db.commit()


# ── Crypto Payment Endpoints ──────────────────────────────────────

@router.post("/api/payment/crypto/request")
def request_crypto_payment(
    body: CryptoRequestBody,
    user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    if body.plan not in ("pro", "lifetime"):
        raise HTTPException(400, "Invalid plan")
    if not settings.crypto_wallet_address:
        raise HTTPException(501, "Crypto payment is not configured")

    plan_cfg = get_plan(body.plan)
    amount_cents = plan_cfg.get("price_monthly_cents") or plan_cfg.get("price_once_cents", 0)
    if amount_cents == 0:
        raise HTTPException(400, "This plan has no crypto price configured")

    memo = f"AXL-{user.id}-{secrets.token_hex(4)}"

    record = PaymentRecord(
        user_id=user.id,
        amount_cents=amount_cents,
        currency="usdt",
        payment_method="crypto",
        payment_ref=body.tx_hash or memo,
        plan=body.plan,
        status="pending",
    )
    db.add(record)

    sub = get_or_create_subscription(user.id, db)
    sub.status = "pending_crypto"
    sub.crypto_payment_ref = memo
    db.commit()
    db.refresh(record)

    return {
        "payment_id": record.id,
        "wallet_address": settings.crypto_wallet_address,
        "network": settings.crypto_wallet_network,
        "amount_usd": amount_cents / 100,
        "memo": memo,
        "status": "pending",
    }


@router.post("/api/payment/crypto/submit-tx")
def submit_crypto_tx(
    payment_id: int,
    tx_hash: str,
    user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    record = db.query(PaymentRecord).filter(
        PaymentRecord.id == payment_id,
        PaymentRecord.user_id == user.id,
    ).first()
    if not record:
        raise HTTPException(404, "Payment not found")
    record.payment_ref = tx_hash
    db.commit()
    return {"ok": True, "status": "pending"}


@router.post("/api/payment/crypto/confirm")
def confirm_crypto_payment(
    body: CryptoConfirmBody,
    admin: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if admin.role != "admin":
        raise HTTPException(403, "Admin access required")

    record = db.query(PaymentRecord).filter(PaymentRecord.id == body.payment_record_id).first()
    if not record:
        raise HTTPException(404, "Payment record not found")
    if record.status == "succeeded":
        raise HTTPException(400, "Payment already confirmed")

    record.status = "succeeded"
    sub = get_or_create_subscription(record.user_id, db)
    activate_plan(sub, record.plan, db)
    db.commit()

    return {"ok": True, "user_id": record.user_id, "plan": record.plan, "status": "active"}
