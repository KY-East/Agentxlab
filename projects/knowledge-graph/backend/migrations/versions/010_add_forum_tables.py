"""Add forum_posts, forum_comments, forum_votes, point_logs tables.

Revision ID: 010
Revises: 009
"""

from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "forum_posts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("zone", sa.String(20), nullable=False, server_default="community", index=True),
        sa.Column("post_type", sa.String(30), nullable=False, server_default="discussion", index=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="open", index=True),
        sa.Column("debate_id", sa.Integer, sa.ForeignKey("debates.id"), nullable=True, index=True),
        sa.Column("spark_id", sa.Integer, sa.ForeignKey("sparks.id"), nullable=True),
        sa.Column("parent_post_id", sa.Integer, sa.ForeignKey("forum_posts.id"), nullable=True),
        sa.Column("discipline_tags", sa.Text, nullable=True),
        sa.Column("vote_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("comment_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_pinned", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "forum_comments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("post_id", sa.Integer, sa.ForeignKey("forum_posts.id"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("forum_comments.id"), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("vote_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("comment_type", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "forum_votes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("target_type", sa.String(10), nullable=False),
        sa.Column("target_id", sa.Integer, nullable=False),
        sa.Column("vote_type", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_vote"),
    )

    op.create_table(
        "point_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("points", sa.Integer, nullable=False),
        sa.Column("reference_type", sa.String(30), nullable=True),
        sa.Column("reference_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("point_logs")
    op.drop_table("forum_votes")
    op.drop_table("forum_comments")
    op.drop_table("forum_posts")
