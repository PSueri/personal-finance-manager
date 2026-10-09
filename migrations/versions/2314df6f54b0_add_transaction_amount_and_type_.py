"""Add transaction amount and type constraints

Revision ID: 2314df6f54b0
Revises: 47a4346290ab
Create Date: 2026-10-09 10:44:27.456276

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2314df6f54b0"
down_revision = "47a4346290ab"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    invalid_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM transaction_history
            WHERE amount_cents <= 0
               OR type NOT IN ('Income', 'Expense')
            """
        )
    ).scalar_one()

    if invalid_count:
        raise RuntimeError(
            f"Cannot apply transaction constraints: "
            f"{invalid_count} existing transactions have "
            f"an invalid amount or type."
        )

    with op.batch_alter_table("transaction_history") as batch_op:
        batch_op.create_check_constraint(
            "ck_transaction_amount_positive",
            "amount_cents > 0",
        )
        batch_op.create_check_constraint(
            "ck_transaction_type_valid",
            "type IN ('Income', 'Expense')",
        )


def downgrade():
    with op.batch_alter_table("transaction_history") as batch_op:
        batch_op.drop_constraint(
            "ck_transaction_type_valid",
            type_="check",
        )
        batch_op.drop_constraint(
            "ck_transaction_amount_positive",
            type_="check",
        )
