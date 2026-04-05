from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Discipline(Base):
    __tablename__ = "disciplines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name_zh: Mapped[str | None] = mapped_column(String(200))
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("disciplines.id"), index=True
    )
    depth: Mapped[int] = mapped_column(Integer, default=0)

    # OpenAlex integration
    openalex_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    level: Mapped[str | None] = mapped_column(
        String(20)
    )  # "field" | "subfield" | "topic"
    description: Mapped[str | None] = mapped_column(String(1000))
    works_count: Mapped[int | None] = mapped_column(Integer)

    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    parent: Mapped[Discipline | None] = relationship(
        "Discipline", remote_side=[id], back_populates="children"
    )
    children: Mapped[list[Discipline]] = relationship(
        "Discipline", back_populates="parent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Discipline {self.name_en}>"
