"""Points & leaderboard endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.points import PointLog
from app.models.user import User
from app.schemas import PointLogOut, LeaderboardEntry
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/points", tags=["points"])


@router.get("/log", response_model=list[PointLogOut])
def my_point_log(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(PointLog)
        .filter(PointLog.user_id == user.id)
        .order_by(desc(PointLog.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [PointLogOut.model_validate(r) for r in rows]


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .filter(User.points > 0)
        .order_by(desc(User.points))
        .limit(limit)
        .all()
    )
    return [
        LeaderboardEntry(
            user_id=u.id,
            display_name=u.display_name,
            avatar_url=u.avatar_url,
            points=u.points,
        )
        for u in users
    ]
