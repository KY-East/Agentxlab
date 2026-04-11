from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from app.models.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    plan = Column(String(20), nullable=False, server_default="free")
    status = Column(String(20), nullable=False, server_default="active")

    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    crypto_payment_ref = Column(String(500), nullable=True)

    monthly_token_limit = Column(Integer, nullable=False, server_default="50000")
    tokens_used_this_month = Column(Integer, nullable=False, server_default="0")
    quota_reset_at = Column(DateTime(timezone=True), nullable=True)

    allowed_models = Column(Text, nullable=True)
    preferred_model = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(10), nullable=False, server_default="usd")
    payment_method = Column(String(20), nullable=False)
    payment_ref = Column(String(500), nullable=True)
    plan = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, server_default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
