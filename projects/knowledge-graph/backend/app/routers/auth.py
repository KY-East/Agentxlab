"""Authentication endpoints — Google OAuth + JWT."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.services.auth import verify_google_token, issue_jwt, get_current_user
from app.services.points import try_daily_login

router = APIRouter(prefix="/api/auth", tags=["auth"])


class GoogleLoginRequest(BaseModel):
    credential: str


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
    created_at: str | None = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: str | None = None
    avatar_url: str | None = None


AuthResponse.model_rebuild()


@router.post("/google", response_model=AuthResponse)
def google_login(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    payload = verify_google_token(body.credential)

    google_sub = payload["sub"]
    email = payload.get("email", "")
    name = payload.get("name", email.split("@")[0])
    picture = payload.get("picture")

    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user is None:
        user = User(
            google_sub=google_sub,
            email=email,
            display_name=name,
            avatar_url=picture,
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


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
def update_me(
    body: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
