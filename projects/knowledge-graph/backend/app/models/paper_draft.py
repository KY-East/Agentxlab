"""PaperDraft and PaperSection models for iterative paper generation."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PaperDraft(Base):
    __tablename__ = "paper_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    debate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("debates.id"), nullable=False, index=True
    )
    direction: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="outline")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    debate: Mapped["Debate"] = relationship(back_populates="paper_drafts")  # noqa: F821
    sections: Mapped[list["PaperSection"]] = relationship(
        back_populates="draft", order_by="PaperSection.sort_order",
        cascade="all, delete-orphan",
    )


class PaperSection(Base):
    __tablename__ = "paper_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    draft_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("paper_drafts.id"), nullable=False, index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    heading: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    writing_instruction: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    draft: Mapped["PaperDraft"] = relationship(back_populates="sections")
