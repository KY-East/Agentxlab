from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

intersection_discipline = Table(
    "intersection_discipline",
    Base.metadata,
    Column(
        "intersection_id", Integer, ForeignKey("intersections.id"), primary_key=True
    ),
    Column("discipline_id", Integer, ForeignKey("disciplines.id"), primary_key=True),
)

intersection_scholar = Table(
    "intersection_scholar",
    Base.metadata,
    Column(
        "intersection_id", Integer, ForeignKey("intersections.id"), primary_key=True
    ),
    Column("scholar_id", Integer, ForeignKey("scholars.id"), primary_key=True),
)

intersection_paper = Table(
    "intersection_paper",
    Base.metadata,
    Column(
        "intersection_id", Integer, ForeignKey("intersections.id"), primary_key=True
    ),
    Column("paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
)


class Intersection(Base):
    __tablename__ = "intersections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # active | gap
    core_tension: Mapped[str | None] = mapped_column(Text)
    classic_dialogue: Mapped[str | None] = mapped_column(Text)
    frontier_progress: Mapped[str | None] = mapped_column(Text)
    open_questions: Mapped[str | None] = mapped_column(Text)

    disciplines = relationship(
        "Discipline", secondary=intersection_discipline, backref="intersections",
        uselist=True,
    )
    scholars = relationship(
        "Scholar", secondary=intersection_scholar, backref="intersections_as_scholar",
        uselist=True,
    )
    papers = relationship(
        "Paper", secondary=intersection_paper, backref="intersections_as_paper",
        uselist=True,
    )

    def __repr__(self) -> str:
        return f"<Intersection {self.title}>"
