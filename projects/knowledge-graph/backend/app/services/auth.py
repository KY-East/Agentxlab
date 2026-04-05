"""Google OAuth verification + JWT issue / decode.

google-auth is an optional dependency — if not installed, the Google login
endpoint will return 501 but the rest of the API stays functional.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

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
