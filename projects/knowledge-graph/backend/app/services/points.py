"""Points system — award, deduct, and query user points."""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.points import PointLog
from app.models.user import User

logger = logging.getLogger(__name__)

POINT_TABLE: dict[str, int] = {
    "daily_login": 5,
    "create_post": 10,
    "create_comment": 3,
    "receive_upvote": 2,
    "claim_experiment": 20,
    "submit_result_verified": 2000,
    "submit_result_falsified_inspiring": 800,
    "submit_result_inconclusive": 50,
    "debate_post_valued": 30,
}


def award_points(
    user_id: int,
    action: str,
    db: Session,
    *,
    points: int | None = None,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> int:
    """Award points for an action. Returns the amount awarded."""
    amt = points if points is not None else POINT_TABLE.get(action, 0)
    if amt == 0:
        return 0

    log = PointLog(
        user_id=user_id,
        action=action,
        points=amt,
        reference_type=ref_type,
        reference_id=ref_id,
    )
    db.add(log)

    user = db.query(User).get(user_id)
    if user:
        user.points = (user.points or 0) + amt

    db.flush()
    logger.info("Awarded %+d points to user %d for '%s'", amt, user_id, action)
    return amt


def try_daily_login(user_id: int, db: Session) -> int:
    """Award daily login points if not already awarded today."""
    today_start = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
    existing = (
        db.query(PointLog)
        .filter(
            PointLog.user_id == user_id,
            PointLog.action == "daily_login",
            PointLog.created_at >= today_start,
        )
        .first()
    )
    if existing:
        return 0
    return award_points(user_id, "daily_login", db)
