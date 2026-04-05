"""Add debate_experiment_meta table.

Revision ID: 008
Revises: 007
"""

from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "debate_experiment_meta",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "debate_id",
            sa.Integer,
            sa.ForeignKey("debates.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("discipline_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("agent_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("round_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("message_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("persona_distribution", sa.Text),
        sa.Column("rank_distribution", sa.Text),
        sa.Column("weight_distribution", sa.Text),
        sa.Column("discipline_names", sa.Text),
        sa.Column("mode", sa.String(20), nullable=False, server_default="free"),
        sa.Column("spark_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_novelty_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("spark_type_distribution", sa.Text),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade():
    op.drop_table("debate_experiment_meta")
