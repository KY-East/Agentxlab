"""Add Final Answer Layer columns to debates.

Phase 2 (2026-04-27): direct answer + why + conditions + next_steps.
4 NULLABLE TEXT fields, debate/free shared schema.

See CHANGELOG 2026-04-27 + notes/design.md §axl-debate-mode-design.
"""

revision = "013"
down_revision = "012"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "debates",
        sa.Column("summary_direct_answer", sa.Text(), nullable=True),
    )
    op.add_column(
        "debates",
        sa.Column("summary_why", sa.Text(), nullable=True),
    )
    op.add_column(
        "debates",
        sa.Column("summary_conditions", sa.Text(), nullable=True),
    )
    op.add_column(
        "debates",
        sa.Column("summary_next_steps", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column("debates", "summary_next_steps")
    op.drop_column("debates", "summary_conditions")
    op.drop_column("debates", "summary_why")
    op.drop_column("debates", "summary_direct_answer")
