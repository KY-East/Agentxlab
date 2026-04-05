from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

debate_discipline = Table(
    "debate_discipline",
    Base.metadata,
    Column("debate_id", Integer, ForeignKey("debates.id"), primary_key=True),
    Column("discipline_id", Integer, ForeignKey("disciplines.id"), primary_key=True),
)


class Debate(Base):
    __tablename__ = "debates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    proposition: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(5), default="zh")
    status: Mapped[str] = mapped_column(String(20), default="active")
    intersection_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("intersections.id"), index=True
    )

    summary_consensus: Mapped[str | None] = mapped_column(Text)
    summary_disagreements: Mapped[str | None] = mapped_column(Text)
    summary_open_questions: Mapped[str | None] = mapped_column(Text)
    summary_directions: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    disciplines = relationship(
        "Discipline", secondary=debate_discipline, uselist=True,
    )
    intersection = relationship("Intersection", uselist=False)
    agents: Mapped[list[DebateAgent]] = relationship(
        back_populates="debate", cascade="all, delete-orphan",
        order_by="DebateAgent.sort_order",
    )
    messages: Mapped[list[DebateMessage]] = relationship(
        back_populates="debate", cascade="all, delete-orphan",
        order_by="DebateMessage.id",
    )
    paper_drafts = relationship(
        "PaperDraft", back_populates="debate", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Debate {self.id} '{self.title}' [{self.mode}]>"


class DebateAgent(Base):
    __tablename__ = "debate_agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    debate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("debates.id"), index=True
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    discipline_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("disciplines.id")
    )
    persona: Mapped[str] = mapped_column(String(50), nullable=False)
    rank: Mapped[str] = mapped_column(String(20), default="professor")
    weight: Mapped[int] = mapped_column(Integer, default=50)
    stance: Mapped[str | None] = mapped_column(String(20))
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    debate: Mapped[Debate] = relationship(back_populates="agents")
    discipline = relationship("Discipline", uselist=False)

    def __repr__(self) -> str:
        return f"<DebateAgent {self.agent_name}>"


class DebateMessage(Base):
    __tablename__ = "debate_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    debate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("debates.id"), index=True
    )
    agent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("debate_agents.id")
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    debate: Mapped[Debate] = relationship(back_populates="messages")
    agent: Mapped[DebateAgent | None] = relationship(uselist=False)

    def __repr__(self) -> str:
        return f"<DebateMessage r{self.round_number} by {self.role}>"
