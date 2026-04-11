"""Authentication endpoints — Google OAuth, Email/Password, JWT."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.services.auth import (
    verify_google_token,
    issue_jwt,
    get_current_user,
    get_verified_user,
    hash_password,
    verify_password,
    generate_token,
    send_verification_email,
    send_reset_email,
)
from app.services.points import try_daily_login

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Schemas ────────────────────────────────────────────────────────

class GoogleLoginRequest(BaseModel):
    credential: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("display_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 50:
            raise ValueError("Display name must be 1-50 characters")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class UserOut(BaseModel):
    id: int
    email: str
    display_name: str
    avatar_url: str | None = None
    did_address: str | None = None
    points: int = 0
    role: str = "user"
    email_verified: bool = False
    created_at: datetime | str | None = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: str | None = None
    avatar_url: str | None = None


AuthResponse.model_rebuild()


# ── Google OAuth ───────────────────────────────────────────────────

@router.post("/google", response_model=AuthResponse)
def google_login(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    payload = verify_google_token(body.credential)

    google_sub = payload["sub"]
    email = payload.get("email", "")
    name = payload.get("name", email.split("@")[0])
    picture = payload.get("picture")

    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user is None:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            existing.google_sub = google_sub
            existing.email_verified = True
            if picture and not existing.avatar_url:
                existing.avatar_url = picture
            user = existing
        else:
            user = User(
                google_sub=google_sub,
                email=email,
                display_name=name,
                avatar_url=picture,
                email_verified=True,
            )
            db.add(user)
    else:
        user.last_login_at = datetime.now(timezone.utc)
        if picture and user.avatar_url != picture:
            user.avatar_url = picture

    db.commit()
    db.refresh(user)

    try_daily_login(user.id, db)
    db.commit()
    db.refresh(user)

    token = issue_jwt(user.id)
    return AuthResponse(token=token, user=UserOut.model_validate(user))


# ── Email / Password Register ─────────────────────────────────────

@router.post("/register", response_model=AuthResponse)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(409, "Email already registered")

    vtok = generate_token()
    user = User(
        google_sub=f"email:{body.email}",
        email=body.email,
        display_name=body.display_name,
        password_hash=hash_password(body.password),
        email_verified=False,
        verify_token=vtok,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    await send_verification_email(user.email, vtok)

    token = issue_jwt(user.id)
    return AuthResponse(token=token, user=UserOut.model_validate(user))


# ── Email / Password Login ────────────────────────────────────────

@router.post("/login", response_model=AuthResponse)
def email_login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.strip().lower()).first()
    if not user or not user.password_hash:
        raise HTTPException(401, "Invalid email or password")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    try_daily_login(user.id, db)
    db.commit()
    db.refresh(user)

    token = issue_jwt(user.id)
    return AuthResponse(token=token, user=UserOut.model_validate(user))


# ── Email Verification ────────────────────────────────────────────

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verify_token == token).first()
    if not user:
        raise HTTPException(400, "Invalid or expired verification link")
    user.email_verified = True
    user.verify_token = None
    db.commit()
    return {"ok": True, "message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.email_verified:
        return {"ok": True, "message": "Already verified"}
    vtok = generate_token()
    user.verify_token = vtok
    db.commit()
    await send_verification_email(user.email, vtok)
    return {"ok": True, "message": "Verification email sent"}


# ── Forgot / Reset Password ───────────────────────────────────────

@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.strip().lower()).first()
    if user and user.password_hash:
        rtok = generate_token()
        user.reset_token = rtok
        user.reset_token_exp = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        await send_reset_email(user.email, rtok)
    return {"ok": True, "message": "If that email exists, a reset link has been sent"}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == body.token).first()
    if not user:
        raise HTTPException(400, "Invalid or expired reset link")
    if user.reset_token_exp and user.reset_token_exp < datetime.now(timezone.utc):
        raise HTTPException(400, "Reset link has expired")
    user.password_hash = hash_password(body.password)
    user.reset_token = None
    user.reset_token_exp = None
    db.commit()
    return {"ok": True, "message": "Password reset successfully"}


# ── Current User ───────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
def update_me(
    body: UserUpdate,
    user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
