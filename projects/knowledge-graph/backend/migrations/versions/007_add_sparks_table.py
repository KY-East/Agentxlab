"""Add sparks table for cross-domain spark capture.

Revision ID: 007
Revises: 006
"""

from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sparks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "debate_id", sa.Integer, sa.ForeignKey("debates.id"), nullable=False, index=True
        ),
        sa.Column(
            "message_id", sa.Integer, sa.ForeignKey("debate_messages.id"), index=True
        ),
        sa.Column("agent_id", sa.Integer, sa.ForeignKey("debate_agents.id")),
        sa.Column(
            "source_discipline_id", sa.Integer, sa.ForeignKey("disciplines.id")
        ),
        sa.Column(
            "target_discipline_id", sa.Integer, sa.ForeignKey("disciplines.id")
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column(
            "novelty_type", sa.String(30), nullable=False, server_default="analogy"
        ),
        sa.Column("novelty_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("reasoning", sa.Text),
        sa.Column(
            "verification_status",
            sa.String(30),
            nullable=False,
            server_default="unverified",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade():
    op.drop_table("sparks")
