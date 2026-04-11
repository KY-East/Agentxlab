"""Authentication: Google OAuth, email/password, JWT, email verification.

google-auth is an optional dependency — if not installed, the Google login
endpoint will return 501 but the rest of the API stays functional.
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

try:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token as google_id_token

    _google_available = True
except ImportError:
    _google_available = False
    logger.warning("google-auth not installed — Google OAuth login will be unavailable")

_bearer = HTTPBearer(auto_error=False)

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30


def verify_google_token(credential: str) -> dict[str, Any]:
    """Verify a Google ID-token and return the payload (sub, email, name, picture …)."""
    if not _google_available:
        raise HTTPException(
            status.HTTP_501_NOT_IMPLEMENTED,
            "Google OAuth is not available (google-auth not installed)",
        )
    try:
        payload = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.google_client_id,
        )
        return payload
    except Exception as exc:
        logger.warning("Google token verification failed: %s", exc)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Google credential") from exc


def issue_jwt(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(user_id), "exp": exp},
        settings.jwt_secret,
        algorithm=JWT_ALGORITHM,
    )


def decode_jwt(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    user_id = decode_jwt(creds.credentials)
    user = db.query(User).get(user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def get_verified_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Like get_current_user but also requires email_verified=True."""
    user = get_current_user(creds, db)
    if not user.email_verified:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Email verification required. Please check your inbox.",
        )
    return user


def get_optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """Same as get_current_user but returns None instead of 401."""
    if creds is None:
        return None
    try:
        user_id = decode_jwt(creds.credentials)
        return db.query(User).get(user_id)
    except HTTPException:
        return None


# ── Password hashing ───────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def generate_token() -> str:
    return secrets.token_urlsafe(32)


# ── Email sending ──────────────────────────────────────────────────

async def send_email(to: str, subject: str, html_body: str) -> None:
    if not settings.smtp_host:
        logger.warning("SMTP not configured, skipping email to %s", to)
        return

    import aiosmtplib

    msg = EmailMessage()
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(html_body, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user or None,
        password=settings.smtp_password or None,
        start_tls=True,
    )


async def send_verification_email(email: str, token: str) -> None:
    link = f"{settings.app_base_url}/verify-email?token={token}"
    html = f"""
    <div style="font-family: monospace; max-width: 480px; margin: 0 auto; padding: 24px; background: #0a0a0a; color: #e5e5e5; border: 2px solid #333;">
      <h2 style="color: #22d3ee; letter-spacing: 0.1em; text-transform: uppercase;">Agent X Lab</h2>
      <p>Click the link below to verify your email:</p>
      <a href="{link}" style="display: inline-block; margin: 16px 0; padding: 10px 24px; border: 2px solid #22d3ee; color: #22d3ee; text-decoration: none; font-family: monospace; text-transform: uppercase; letter-spacing: 0.05em;">
        VERIFY EMAIL
      </a>
      <p style="color: #666; font-size: 12px;">If the button doesn't work, copy this URL: {link}</p>
    </div>
    """
    await send_email(email, "Verify your email — Agent X Lab", html)


async def send_reset_email(email: str, token: str) -> None:
    link = f"{settings.app_base_url}/reset-password?token={token}"
    html = f"""
    <div style="font-family: monospace; max-width: 480px; margin: 0 auto; padding: 24px; background: #0a0a0a; color: #e5e5e5; border: 2px solid #333;">
      <h2 style="color: #22d3ee; letter-spacing: 0.1em; text-transform: uppercase;">Agent X Lab</h2>
      <p>Click the link below to reset your password:</p>
      <a href="{link}" style="display: inline-block; margin: 16px 0; padding: 10px 24px; border: 2px solid #22d3ee; color: #22d3ee; text-decoration: none; font-family: monospace; text-transform: uppercase; letter-spacing: 0.05em;">
        RESET PASSWORD
      </a>
      <p style="color: #666; font-size: 12px;">This link expires in 1 hour. If you didn't request a reset, ignore this email.</p>
    </div>
    """
    await send_email(email, "Reset your password — Agent X Lab", html)
