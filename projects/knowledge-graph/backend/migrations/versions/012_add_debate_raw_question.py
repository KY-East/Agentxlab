"""Add raw_question + suggested_dimensions to debates.

Root-cause fix for lost user input. See CHANGELOG 2026-04-15.
"""

revision = "012"
down_revision = "011"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "debates",
        sa.Column("raw_question", sa.Text(), nullable=True),
    )
    op.add_column(
        "debates",
        sa.Column("suggested_dimensions", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column("debates", "suggested_dimensions")
    op.drop_column("debates", "raw_question")
