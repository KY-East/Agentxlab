"""Experiment metadata for tracking debate conditions and spark outcomes."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DebateExperimentMeta(Base):
    __tablename__ = "debate_experiment_meta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    debate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("debates.id"), unique=True, index=True, nullable=False
    )

    discipline_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    agent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    round_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    persona_distribution: Mapped[str | None] = mapped_column(Text)
    rank_distribution: Mapped[str | None] = mapped_column(Text)
    weight_distribution: Mapped[str | None] = mapped_column(Text)
    discipline_names: Mapped[str | None] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(20), nullable=False, default="free")

    spark_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_novelty_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    spark_type_distribution: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    debate = relationship("Debate", uselist=False)

    def __repr__(self) -> str:
        return f"<ExperimentMeta debate={self.debate_id} sparks={self.spark_count}>"
