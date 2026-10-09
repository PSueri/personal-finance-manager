"""Require populated transaction categories

Revision ID: 969efbb5ddb7
Revises: 2314df6f54b0
Create Date: 2026-10-09 12:22:22.914927

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "969efbb5ddb7"
down_revision = "2314df6f54b0"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    invalid_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM transaction_history
            WHERE first_category IS NULL
               OR length(trim(first_category)) = 0
               OR trim(first_category) = 'Select'
               OR second_category IS NULL
               OR length(trim(second_category)) = 0
               OR trim(second_category) = 'Select'
            """
        )
    ).scalar_one()

    if invalid_count:
        raise RuntimeError(
            f"Cannot apply category constraints: "
            f"{invalid_count} existing transactions have "
            f"an empty or placeholder category."
        )

    with op.batch_alter_table("transaction_history") as batch_op:
        batch_op.create_check_constraint(
            "ck_transaction_first_category_required",
            "length(trim(first_category)) > 0 AND trim(first_category) <> 'Select'",
        )
        batch_op.create_check_constraint(
            "ck_transaction_second_category_required",
            "length(trim(second_category)) > 0 AND trim(second_category) <> 'Select'",
        )


def downgrade():
    with op.batch_alter_table("transaction_history") as batch_op:
        batch_op.drop_constraint(
            "ck_transaction_second_category_required",
            type_="check",
        )
        batch_op.drop_constraint(
            "ck_transaction_first_category_required",
            type_="check",
        )
