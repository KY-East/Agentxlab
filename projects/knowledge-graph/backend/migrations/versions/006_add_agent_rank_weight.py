"""Add rank and weight columns to debate_agents.

Revision ID: 006
Revises: 005
"""

from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "debate_agents",
        sa.Column("rank", sa.String(20), nullable=False, server_default="professor"),
    )
    op.add_column(
        "debate_agents",
        sa.Column("weight", sa.Integer, nullable=False, server_default="50"),
    )


def downgrade():
    op.drop_column("debate_agents", "weight")
    op.drop_column("debate_agents", "rank")
