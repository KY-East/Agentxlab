"""API endpoints for querying cross-domain sparks and experiment data."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.spark import Spark
from app.models.experiment import DebateExperimentMeta
from app.schemas import ExperimentMetaOut, SparkOut

router = APIRouter(prefix="/api/sparks", tags=["sparks"])


@router.get("", response_model=list[SparkOut])
def list_sparks(
    debate_id: int | None = Query(None),
    discipline_id: int | None = Query(None),
    min_score: float | None = Query(None, ge=0, le=1),
    novelty_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List sparks with optional filters."""
    q = db.query(Spark).order_by(Spark.novelty_score.desc(), Spark.id.desc())

    if debate_id is not None:
        q = q.filter(Spark.debate_id == debate_id)
    if discipline_id is not None:
        q = q.filter(
            (Spark.source_discipline_id == discipline_id)
            | (Spark.target_discipline_id == discipline_id)
        )
    if min_score is not None:
        q = q.filter(Spark.novelty_score >= min_score)
    if novelty_type is not None:
        q = q.filter(Spark.novelty_type == novelty_type)

    return [SparkOut.model_validate(s) for s in q.offset(offset).limit(limit).all()]


@router.get("/stats")
def spark_stats(
    debate_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """Aggregate spark statistics."""
    from sqlalchemy import func

    q = db.query(Spark)
    if debate_id is not None:
        q = q.filter(Spark.debate_id == debate_id)

    total = q.count()
    if total == 0:
        return {
            "total": 0,
            "avg_score": 0,
            "by_type": {},
            "by_verification": {},
        }

    avg_score = q.with_entities(func.avg(Spark.novelty_score)).scalar() or 0

    by_type = dict(
        q.with_entities(Spark.novelty_type, func.count())
        .group_by(Spark.novelty_type)
        .all()
    )

    by_verification = dict(
        q.with_entities(Spark.verification_status, func.count())
        .group_by(Spark.verification_status)
        .all()
    )

    return {
        "total": total,
        "avg_score": round(float(avg_score), 3),
        "by_type": by_type,
        "by_verification": by_verification,
    }


# ── Experiment meta endpoints ──


@router.get("/experiments", response_model=list[ExperimentMetaOut])
def list_experiments(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all experiment metadata records, newest first."""
    q = (
        db.query(DebateExperimentMeta)
        .order_by(DebateExperimentMeta.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return [ExperimentMetaOut.model_validate(m) for m in q.all()]


@router.get("/experiments/{debate_id}", response_model=ExperimentMetaOut)
def get_experiment(debate_id: int, db: Session = Depends(get_db)):
    """Get experiment metadata for a specific debate."""
    meta = (
        db.query(DebateExperimentMeta)
        .filter(DebateExperimentMeta.debate_id == debate_id)
        .first()
    )
    if not meta:
        raise HTTPException(404, "No experiment metadata for this debate")
    return ExperimentMetaOut.model_validate(meta)
