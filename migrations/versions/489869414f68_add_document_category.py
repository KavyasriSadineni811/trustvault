"""Add document category

Revision ID: 489869414f68
Revises: 81f735534421
Create Date: 2026-10-22
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "489869414f68"
down_revision = "81f735534421"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "documents",
        sa.Column(
            "category",
            sa.String(length=50),
            nullable=True
        )
    )

    op.create_index(
        "ix_documents_category",
        "documents",
        ["category"]
    )


def downgrade():
    op.drop_index(
        "ix_documents_category",
        table_name="documents"
    )

    op.drop_column(
        "documents",
        "category"
    )