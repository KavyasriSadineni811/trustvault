
"""Add tamper evident audit fields

Revision ID: 81f735534421
Revises: 1b5d61188610
Create Date: 2026-10-22
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "81f735534421"
down_revision = "1b5d61188610"
branch_labels = None
depends_on = None


def upgrade():

    # ==========================================================
    # STEP 1
    # Add new columns as nullable first.
    #
    # Existing audit records do not have values for these
    # columns, so they cannot initially be NOT NULL.
    # ==========================================================

    with op.batch_alter_table(
        "audit_logs",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "details",
                sa.Text(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "previous_hash",
                sa.String(length=64),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "record_hash",
                sa.String(length=64),
                nullable=True
            )
        )

        # Existing audit records must remain valid.
        # Therefore we do NOT make record_hash NOT NULL
        # during this migration.


def downgrade():

    with op.batch_alter_table(
        "audit_logs",
        schema=None
    ) as batch_op:

        batch_op.drop_column(
            "record_hash"
        )

        batch_op.drop_column(
            "previous_hash"
        )

        batch_op.drop_column(
            "details"
        )
