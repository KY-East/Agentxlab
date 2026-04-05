from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.discipline import Discipline

scholar_discipline = Table(
    "scholar_discipline",
    Base.metadata,
    Column("scholar_id", Integer, ForeignKey("scholars.id"), primary_key=True),
    Column("discipline_id", Integer, ForeignKey("disciplines.id"), primary_key=True),
)


class Scholar(Base):
    __tablename__ = "scholars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    era: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text)
    contribution: Mapped[str | None] = mapped_column(Text)

    # OpenAlex integration
    openalex_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    orcid: Mapped[str | None] = mapped_column(String(50))
    affiliation: Mapped[str | None] = mapped_column(String(500))
    works_count: Mapped[int | None] = mapped_column(Integer)
    cited_by_count: Mapped[int | None] = mapped_column(Integer)

    disciplines = relationship(
        "Discipline", secondary=scholar_discipline, backref="scholars",
        uselist=True,
    )

    def __repr__(self) -> str:
        return f"<Scholar {self.name}>"
