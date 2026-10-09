from datetime import datetime

from application.extensions import db


class TransactionHistory(db.Model):
    __table_args__ = (
        db.CheckConstraint(
            "amount_cents > 0",
            name="ck_transaction_amount_positive",
        ),
        db.CheckConstraint(
            "type IN ('Income', 'Expense')",
            name="ck_transaction_type_valid",
        ),
        db.CheckConstraint(
            "length(trim(first_category)) > 0 AND trim(first_category) <> 'Select'",
            name="ck_transaction_first_category_required",
        ),
        db.CheckConstraint(
            "length(trim(second_category)) > 0 AND trim(second_category) <> 'Select'",
            name="ck_transaction_second_category_required",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), nullable=False)
    first_category = db.Column(db.String(30), nullable=False)
    second_category = db.Column(db.String(30), nullable=False)
    date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    amount_cents = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return str(self.id)
