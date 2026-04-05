"""Add paper_discipline many-to-many table.

Revision ID: 005
Revises: 004
"""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "paper_discipline",
        sa.Column("paper_id", sa.Integer, sa.ForeignKey("papers.id"), primary_key=True),
        sa.Column("discipline_id", sa.Integer, sa.ForeignKey("disciplines.id"), primary_key=True),
        sa.Column("score", sa.Integer, default=0),
    )


def downgrade():
    op.drop_table("paper_discipline")
