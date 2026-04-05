"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "disciplines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name_en", sa.String(200), nullable=False, unique=True),
        sa.Column("name_zh", sa.String(200)),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("disciplines.id")),
        sa.Column("depth", sa.Integer(), default=0),
    )
    op.create_index("ix_disciplines_parent_id", "disciplines", ["parent_id"])

    op.create_table(
        "scholars",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("era", sa.String(100)),
        sa.Column("bio", sa.Text()),
        sa.Column("contribution", sa.Text()),
    )

    op.create_table(
        "scholar_discipline",
        sa.Column(
            "scholar_id",
            sa.Integer(),
            sa.ForeignKey("scholars.id"),
            primary_key=True,
        ),
        sa.Column(
            "discipline_id",
            sa.Integer(),
            sa.ForeignKey("disciplines.id"),
            primary_key=True,
        ),
    )

    op.create_table(
        "papers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("year", sa.Integer()),
        sa.Column("doi_or_url", sa.String(500)),
        sa.Column("paper_type", sa.String(20), server_default="classic"),
        sa.Column("abstract", sa.Text()),
        sa.Column("source", sa.String(300)),
    )

    op.create_table(
        "paper_author",
        sa.Column(
            "paper_id", sa.Integer(), sa.ForeignKey("papers.id"), primary_key=True
        ),
        sa.Column(
            "scholar_id",
            sa.Integer(),
            sa.ForeignKey("scholars.id"),
            primary_key=True,
        ),
    )

    op.create_table(
        "intersections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("core_tension", sa.Text()),
        sa.Column("classic_dialogue", sa.Text()),
        sa.Column("frontier_progress", sa.Text()),
        sa.Column("open_questions", sa.Text()),
    )

    op.create_table(
        "intersection_discipline",
        sa.Column(
            "intersection_id",
            sa.Integer(),
            sa.ForeignKey("intersections.id"),
            primary_key=True,
        ),
        sa.Column(
            "discipline_id",
            sa.Integer(),
            sa.ForeignKey("disciplines.id"),
            primary_key=True,
        ),
    )

    op.create_table(
        "intersection_scholar",
        sa.Column(
            "intersection_id",
            sa.Integer(),
            sa.ForeignKey("intersections.id"),
            primary_key=True,
        ),
        sa.Column(
            "scholar_id",
            sa.Integer(),
            sa.ForeignKey("scholars.id"),
            primary_key=True,
        ),
    )

    op.create_table(
        "intersection_paper",
        sa.Column(
            "intersection_id",
            sa.Integer(),
            sa.ForeignKey("intersections.id"),
            primary_key=True,
        ),
        sa.Column(
            "paper_id", sa.Integer(), sa.ForeignKey("papers.id"), primary_key=True
        ),
    )

    op.create_table(
        "ai_hypotheses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "intersection_id",
            sa.Integer(),
            sa.ForeignKey("intersections.id"),
            index=True,
        ),
        sa.Column("model_name", sa.String(100)),
        sa.Column("prompt_used", sa.Text()),
        sa.Column("hypothesis_text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("ai_hypotheses")
    op.drop_table("intersection_paper")
    op.drop_table("intersection_scholar")
    op.drop_table("intersection_discipline")
    op.drop_table("intersections")
    op.drop_table("paper_author")
    op.drop_table("papers")
    op.drop_table("scholar_discipline")
    op.drop_table("scholars")
    op.drop_index("ix_disciplines_parent_id", "disciplines")
    op.drop_table("disciplines")
