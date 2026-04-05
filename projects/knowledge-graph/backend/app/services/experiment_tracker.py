"""Automatically record experiment metadata when a debate completes."""

from __future__ import annotations

import json
import logging
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.models.debate import Debate
from app.models.experiment import DebateExperimentMeta
from app.models.spark import Spark

logger = logging.getLogger(__name__)


def record_experiment_meta(debate: Debate, db: Session) -> DebateExperimentMeta:
    """Snapshot experimental variables and spark outcomes for a completed debate."""
    existing = (
        db.query(DebateExperimentMeta)
        .filter(DebateExperimentMeta.debate_id == debate.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.flush()

    non_mod_agents = [a for a in debate.agents if a.persona != "moderator"]

    persona_counts = Counter(a.persona for a in non_mod_agents)
    rank_counts = Counter(a.rank for a in non_mod_agents)
    weight_counts = {
        str(a.discipline_id): a.weight
        for a in non_mod_agents if a.discipline_id
    }
    disc_names = [d.name_en for d in debate.disciplines]

    round_count = 0
    if debate.messages:
        round_count = max(m.round_number for m in debate.messages)

    sparks = db.query(Spark).filter(Spark.debate_id == debate.id).all()
    spark_count = len(sparks)
    avg_score = 0.0
    spark_type_counts: dict[str, int] = {}
    if sparks:
        avg_score = sum(s.novelty_score for s in sparks) / len(sparks)
        spark_type_counts = dict(Counter(s.novelty_type for s in sparks))

    meta = DebateExperimentMeta(
        debate_id=debate.id,
        discipline_count=len(debate.disciplines),
        agent_count=len(non_mod_agents),
        round_count=round_count,
        message_count=len(debate.messages),
        persona_distribution=json.dumps(dict(persona_counts)),
        rank_distribution=json.dumps(dict(rank_counts)),
        weight_distribution=json.dumps(weight_counts),
        discipline_names=json.dumps(disc_names),
        mode=debate.mode,
        spark_count=spark_count,
        avg_novelty_score=round(avg_score, 4),
        spark_type_distribution=json.dumps(spark_type_counts) if spark_type_counts else None,
    )
    db.add(meta)
    db.flush()

    logger.info(
        "Recorded experiment meta for debate %d: %d sparks, avg_score=%.3f",
        debate.id, spark_count, avg_score,
    )
    return meta
