from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AIHypothesis(Base):
    __tablename__ = "ai_hypotheses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    intersection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("intersections.id"), index=True
    )
    model_name: Mapped[str] = mapped_column(String(100))
    prompt_used: Mapped[str | None] = mapped_column(Text)
    hypothesis_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    intersection: Mapped["Intersection"] = relationship(
        "Intersection", backref="hypotheses"
    )

    def __repr__(self) -> str:
        return f"<AIHypothesis intersection={self.intersection_id}>"
