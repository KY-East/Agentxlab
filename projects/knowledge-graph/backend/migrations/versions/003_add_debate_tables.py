"""add debate tables (debates, debate_agents, debate_messages, debate_discipline)

Revision ID: 003
Revises: 002
Create Date: 2026-04-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "debates",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("proposition", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("intersection_id", sa.Integer, sa.ForeignKey("intersections.id"), nullable=True),
        sa.Column("summary_consensus", sa.Text, nullable=True),
        sa.Column("summary_disagreements", sa.Text, nullable=True),
        sa.Column("summary_open_questions", sa.Text, nullable=True),
        sa.Column("summary_directions", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_debates_intersection_id", "debates", ["intersection_id"])

    op.create_table(
        "debate_discipline",
        sa.Column("debate_id", sa.Integer, sa.ForeignKey("debates.id"), primary_key=True),
        sa.Column("discipline_id", sa.Integer, sa.ForeignKey("disciplines.id"), primary_key=True),
    )

    op.create_table(
        "debate_agents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("debate_id", sa.Integer, sa.ForeignKey("debates.id"), nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("discipline_id", sa.Integer, sa.ForeignKey("disciplines.id"), nullable=True),
        sa.Column("persona", sa.String(50), nullable=False),
        sa.Column("stance", sa.String(20), nullable=True),
        sa.Column("system_prompt", sa.Text, nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index("ix_debate_agents_debate_id", "debate_agents", ["debate_id"])

    op.create_table(
        "debate_messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("debate_id", sa.Integer, sa.ForeignKey("debates.id"), nullable=False),
        sa.Column("agent_id", sa.Integer, sa.ForeignKey("debate_agents.id"), nullable=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("round_number", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_debate_messages_debate_id", "debate_messages", ["debate_id"])


def downgrade() -> None:
    op.drop_table("debate_messages")
    op.drop_table("debate_agents")
    op.drop_table("debate_discipline")
    op.drop_table("debates")
