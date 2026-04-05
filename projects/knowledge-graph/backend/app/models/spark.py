"""Cross-domain spark captured during agent debates."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Spark(Base):
    __tablename__ = "sparks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    debate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("debates.id"), index=True, nullable=False
    )
    message_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("debate_messages.id"), index=True
    )
    agent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("debate_agents.id")
    )
    source_discipline_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("disciplines.id")
    )
    target_discipline_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("disciplines.id")
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    novelty_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="analogy"
    )
    novelty_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reasoning: Mapped[str | None] = mapped_column(Text)

    verification_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="unverified"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    debate = relationship("Debate", uselist=False)
    message = relationship("DebateMessage", uselist=False)
    agent = relationship("DebateAgent", uselist=False)
    source_discipline = relationship(
        "Discipline", foreign_keys=[source_discipline_id], uselist=False
    )
    target_discipline = relationship(
        "Discipline", foreign_keys=[target_discipline_id], uselist=False
    )

    def __repr__(self) -> str:
        return f"<Spark {self.id} [{self.novelty_type}] score={self.novelty_score:.2f}>"
