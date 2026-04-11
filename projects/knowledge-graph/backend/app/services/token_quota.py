"""Token quota management: check, consume, reset on demand."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.plan_config import get_plan

logger = logging.getLogger(__name__)


def get_or_create_sub(user_id: int, db: Session) -> Subscription:
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


def maybe_reset_quota(sub: Subscription, db: Session) -> None:
    now = datetime.now(timezone.utc)
    if sub.quota_reset_at and sub.quota_reset_at < now:
        sub.tokens_used_this_month = 0
        sub.quota_reset_at = now + timedelta(days=30)
        db.commit()
        logger.info("Quota reset for user %d (plan=%s)", sub.user_id, sub.plan)


def check_quota(user_id: int, db: Session) -> Subscription:
    sub = get_or_create_sub(user_id, db)
    maybe_reset_quota(sub, db)

    if sub.status not in ("active",):
        raise HTTPException(403, "Subscription is not active")

    if sub.tokens_used_this_month >= sub.monthly_token_limit:
        raise HTTPException(
            429,
            f"Monthly token limit reached ({sub.tokens_used_this_month}/{sub.monthly_token_limit}). "
            f"Upgrade your plan for more tokens.",
        )
    return sub


def validate_model(sub: Subscription, requested_model: str | None) -> str:
    allowed = []
    if sub.allowed_models:
        try:
            allowed = json.loads(sub.allowed_models)
        except (json.JSONDecodeError, TypeError):
            allowed = []

    if not requested_model:
        return sub.preferred_model or (allowed[0] if allowed else "deepseek/deepseek-chat")

    if requested_model not in allowed:
        raise HTTPException(
            403,
            f"Model '{requested_model}' is not available on your {sub.plan} plan. "
            f"Available: {', '.join(allowed)}",
        )
    return requested_model


def record_usage(sub: Subscription, tokens_used: int, db: Session) -> int:
    sub.tokens_used_this_month += tokens_used
    db.commit()
    remaining = max(0, sub.monthly_token_limit - sub.tokens_used_this_month)
    return remaining
