from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Intersection, intersection_discipline
from app.schemas import IntersectionBrief, IntersectionOut, IntersectionQuery

router = APIRouter(prefix="/api/intersections", tags=["intersections"])


@router.get("", response_model=list[IntersectionBrief])
def list_intersections(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Intersection)
    if status:
        q = q.filter(Intersection.status == status)
    return [IntersectionBrief.model_validate(ix) for ix in q.all()]


@router.get("/{intersection_id}", response_model=IntersectionOut)
def get_intersection(intersection_id: int, db: Session = Depends(get_db)):
    ix = db.query(Intersection).get(intersection_id)
    if not ix:
        raise HTTPException(404, "Intersection not found")
    return IntersectionOut.model_validate(ix)


@router.post("/query", response_model=list[IntersectionOut])
def query_intersections(body: IntersectionQuery, db: Session = Depends(get_db)):
    """Find intersections that involve ALL of the given discipline ids."""
    if not body.discipline_ids:
        return []

    from sqlalchemy import func

    unique_ids = list(set(body.discipline_ids))
    n = len(unique_ids)

    match_subq = (
        db.query(intersection_discipline.c.intersection_id)
        .filter(intersection_discipline.c.discipline_id.in_(unique_ids))
        .group_by(intersection_discipline.c.intersection_id)
        .having(func.count() == n)
        .subquery()
    )

    total_subq = (
        db.query(
            intersection_discipline.c.intersection_id,
            func.count().label("total"),
        )
        .group_by(intersection_discipline.c.intersection_id)
        .subquery()
    )

    results = (
        db.query(Intersection)
        .join(match_subq, Intersection.id == match_subq.c.intersection_id)
        .join(total_subq, Intersection.id == total_subq.c.intersection_id)
        .filter(total_subq.c.total == n)
        .all()
    )
    return [IntersectionOut.model_validate(ix) for ix in results]
