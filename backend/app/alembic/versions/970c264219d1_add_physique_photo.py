"""Add Physique Photo

Revision ID: 970c264219d1
Revises: 959a1168f860
Create Date: 2026-09-29 22:02:08.476205

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "970c264219d1"
down_revision = "959a1168f860"
branch_labels = None
depends_on = None


def upgrade():
    # Create physique photo table
    op.create_table(
        "physiquephoto",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "photo_type",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "photo_url",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create index for user_id
    op.create_index(
        op.f("ix_physiquephoto_user_id"),
        "physiquephoto",
        ["user_id"],
        unique=False,
    )


def downgrade():
    # Remove index
    op.drop_index(
        op.f("ix_physiquephoto_user_id"),
        table_name="physiquephoto",
    )

    # Remove physique photo table
    op.drop_table("physiquephoto")