"""Add language column to debates table."""

revision = "011"
down_revision = "010"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("debates", sa.Column("language", sa.String(5), server_default="zh", nullable=False))


def downgrade():
    op.drop_column("debates", "language")
