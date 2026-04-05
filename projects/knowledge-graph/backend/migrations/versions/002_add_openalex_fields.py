"""add openalex fields to disciplines, scholars, papers

Revision ID: 002
Revises: 001
Create Date: 2026-04-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Discipline: openalex_id, level, description, works_count
    with op.batch_alter_table("disciplines") as batch_op:
        batch_op.add_column(sa.Column("openalex_id", sa.String(100)))
        batch_op.add_column(sa.Column("level", sa.String(20)))
        batch_op.add_column(sa.Column("description", sa.String(1000)))
        batch_op.add_column(sa.Column("works_count", sa.Integer()))
        batch_op.create_unique_constraint("uq_disciplines_openalex_id", ["openalex_id"])

    # Scholar: openalex_id, orcid, affiliation, works_count, cited_by_count
    with op.batch_alter_table("scholars") as batch_op:
        batch_op.add_column(sa.Column("openalex_id", sa.String(100)))
        batch_op.add_column(sa.Column("orcid", sa.String(50)))
        batch_op.add_column(sa.Column("affiliation", sa.String(500)))
        batch_op.add_column(sa.Column("works_count", sa.Integer()))
        batch_op.add_column(sa.Column("cited_by_count", sa.Integer()))
        batch_op.create_unique_constraint("uq_scholars_openalex_id", ["openalex_id"])

    # Paper: openalex_id, doi, citation_count, published_year
    with op.batch_alter_table("papers") as batch_op:
        batch_op.add_column(sa.Column("openalex_id", sa.String(100)))
        batch_op.add_column(sa.Column("doi", sa.String(200)))
        batch_op.add_column(sa.Column("citation_count", sa.Integer()))
        batch_op.add_column(sa.Column("published_year", sa.Integer()))
        batch_op.create_unique_constraint("uq_papers_openalex_id", ["openalex_id"])


def downgrade() -> None:
    with op.batch_alter_table("papers") as batch_op:
        batch_op.drop_column("published_year")
        batch_op.drop_column("citation_count")
        batch_op.drop_column("doi")
        batch_op.drop_column("openalex_id")

    with op.batch_alter_table("scholars") as batch_op:
        batch_op.drop_column("cited_by_count")
        batch_op.drop_column("works_count")
        batch_op.drop_column("affiliation")
        batch_op.drop_column("orcid")
        batch_op.drop_column("openalex_id")

    with op.batch_alter_table("disciplines") as batch_op:
        batch_op.drop_column("works_count")
        batch_op.drop_column("description")
        batch_op.drop_column("level")
        batch_op.drop_column("openalex_id")
