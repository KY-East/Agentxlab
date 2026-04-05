from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

paper_author = Table(
    "paper_author",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
    Column("scholar_id", Integer, ForeignKey("scholars.id"), primary_key=True),
)

paper_discipline = Table(
    "paper_discipline",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
    Column("discipline_id", Integer, ForeignKey("disciplines.id"), primary_key=True),
    Column("score", Integer, default=0),
)


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)
    doi_or_url: Mapped[str | None] = mapped_column(String(500))
    paper_type: Mapped[str] = mapped_column(
        String(20), default="classic"
    )  # classic | frontier
    abstract: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(300))

    # OpenAlex integration
    openalex_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    doi: Mapped[str | None] = mapped_column(String(200))
    citation_count: Mapped[int | None] = mapped_column(Integer)
    published_year: Mapped[int | None] = mapped_column(Integer)

    authors = relationship(
        "Scholar", secondary=paper_author, backref="papers",
        uselist=True,
    )
    disciplines = relationship(
        "Discipline", secondary=paper_discipline, backref="papers",
        uselist=True,
    )

    def __repr__(self) -> str:
        return f"<Paper {self.title[:50]}>"
