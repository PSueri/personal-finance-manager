from datetime import datetime

from sqlalchemy.exc import IntegrityError

from application.extensions import db
from application.models import TransactionHistory
from tests.base import DatabaseTestCase


class TestTransactionConstraints(DatabaseTestCase):
    def make_transaction(self, **changes):
        values = {
            "type": "Income",
            "first_category": "Work",
            "second_category": "Salary",
            "date": datetime(2024, 3, 15),
            "amount_cents": 100,
        }
        values.update(changes)

        return TransactionHistory(**values)

    def test_database_rejects_invalid_amounts_and_types(self):
        invalid_values = [
            {"amount_cents": 0},
            {"amount_cents": -100},
            {"type": ""},
            {"type": "Select"},
            {"type": "Transfer"},
        ]

        for changes in invalid_values:
            with self.subTest(changes=changes):
                db.session.add(self.make_transaction(**changes))

                try:
                    with self.assertRaises(IntegrityError):
                        db.session.commit()
                finally:
                    db.session.rollback()

                self.assertEqual(TransactionHistory.query.count(), 0)

    def test_database_accepts_valid_transactions(self):
        entries = [
            self.make_transaction(amount_cents=1),
            self.make_transaction(
                type="Expense",
                first_category="Food",
                second_category="Grocery",
                amount_cents=1250,
            ),
        ]

        db.session.add_all(entries)
        db.session.commit()

        self.assertEqual(TransactionHistory.query.count(), 2)
