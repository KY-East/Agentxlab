"""add paper_drafts and paper_sections tables

Revision ID: 004
Revises: 003
Create Date: 2026-04-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "paper_drafts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("debate_id", sa.Integer, sa.ForeignKey("debates.id"), nullable=False, index=True),
        sa.Column("direction", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), server_default="outline"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "paper_sections",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("draft_id", sa.Integer, sa.ForeignKey("paper_drafts.id"), nullable=False, index=True),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("heading", sa.String(300), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("writing_instruction", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("paper_sections")
    op.drop_table("paper_drafts")
