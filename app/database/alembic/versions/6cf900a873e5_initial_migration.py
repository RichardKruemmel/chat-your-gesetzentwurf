"""Initial migration

Revision ID: 6cf900a873e5
Revises: 
Create Date: 2023-10-10 15:52:50.816085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6cf900a873e5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "document",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("pdf_data", sa.LargeBinary(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_id"), "document", ["id"], unique=False)
    op.create_index(op.f("ix_document_label"), "document", ["label"], unique=False)
    op.create_table(
        "election",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("previous_election_id", sa.Integer(), nullable=False),
        sa.Column("election_date", sa.Date(), nullable=False),
        sa.Column("start_date_period", sa.Date(), nullable=False),
        sa.Column("end_date_period", sa.Date(), nullable=False),
        sa.Column("parliament_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["parliament_id"], ["parliament.id"], use_alter=True),
        sa.ForeignKeyConstraint(
            ["previous_election_id"],
            ["election.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "parliament",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("abgeordnetenwatch_url", sa.String(), nullable=False),
        sa.Column("label_long", sa.String(), nullable=False),
        sa.Column("last_election_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["last_election_id"], ["election.id"], use_alter=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "party",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("short_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "election_program",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("election_id", sa.Integer(), nullable=False),
        sa.Column("party_id", sa.Integer(), nullable=False),
        sa.Column("abgeordnetenwatch_file_url", sa.String(), nullable=False),
        sa.Column("file_cloud_url", sa.String(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["document.id"], use_alter=True),
        sa.ForeignKeyConstraint(
            ["election_id"],
            ["election.id"],
        ),
        sa.ForeignKeyConstraint(
            ["party_id"],
            ["party.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_election_program_document_id"),
        "election_program",
        ["document_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_election_program_election_id"),
        "election_program",
        ["election_id"],
        unique=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_election_program_election_id"), table_name="election_program"
    )
    op.drop_index(
        op.f("ix_election_program_document_id"), table_name="election_program"
    )
    op.drop_table("election_program")
    op.drop_table("party")
    op.drop_table("parliament")
    op.drop_table("election")
    op.drop_index(op.f("ix_document_label"), table_name="document")
    op.drop_index(op.f("ix_document_id"), table_name="document")
    op.drop_table("document")
    # ### end Alembic commands ###
