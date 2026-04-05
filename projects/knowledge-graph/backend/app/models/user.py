from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, func

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    google_sub = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(320), nullable=False)
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)

    # Web3 / DID — reserved
    did_address = Column(String(255), nullable=True)
    did_provider = Column(String(50), nullable=True)

    points = Column(Integer, nullable=False, server_default="0")
    role = Column(String(20), nullable=False, server_default="user")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), onupdate=func.now())
