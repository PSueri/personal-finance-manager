import unittest
from datetime import date, datetime

from application.extensions import db
from application.models import TransactionHistory
from application.reporting import get_monthly_cashflow
from tests.base import DatabaseTestCase


class TestMonthlyCashflow(DatabaseTestCase):

    def add_transaction(self, transaction_type, amount, transaction_date):
        is_income = transaction_type == "Income"

        transaction = TransactionHistory(
            type=transaction_type,
            first_category="Work" if is_income else "Food",
            second_category="Salary" if is_income else "Grocery",
            amount_cents=amount,
            date=transaction_date,
        )

        db.session.add(transaction)

    def test_empty_database_returns_twelve_zero_values(self):
        result = get_monthly_cashflow(date(2024, 3, 31))

        self.assertEqual(len(result["labels"]), 12)
        self.assertEqual(result["income"], [0] * 12)
        self.assertEqual(result["expense"], [0] * 12)
        self.assertEqual(result["netflow"], [0] * 12)

    def test_transactions_are_summed_by_month(self):
        self.add_transaction(
            "Income", 1000, datetime(2024, 2, 15)
        )
        self.add_transaction(
            "Income", 500, datetime(2024, 2, 16)
        )
        self.add_transaction(
            "Expense", 200, datetime(2024, 2, 20)
        )
        self.add_transaction(
            "Expense", 75, datetime(2024, 3, 5)
        )
        db.session.commit()

        result = get_monthly_cashflow(date(2024, 3, 31))

        self.assertEqual(result["income"], [0] * 10 + [1500, 0])
        self.assertEqual(result["expense"], [0] * 10 + [200, 75])
        self.assertEqual(result["netflow"], [0] * 10 + [1300, -75])

    def test_only_transactions_inside_the_month_range_are_included(self):
        self.add_transaction(
            "Income", 9000, datetime(2023, 3, 31, 23, 59, 59)
        )
        self.add_transaction(
            "Income", 100, datetime(2023, 4, 1)
        )
        self.add_transaction(
            "Expense", 25, datetime(2024, 3, 31, 23, 59, 59)
        )
        self.add_transaction(
            "Expense", 8000, datetime(2024, 4, 1)
        )
        db.session.commit()

        result = get_monthly_cashflow(date(2024, 3, 31))

        self.assertEqual(result["income"], [100] + [0] * 11)
        self.assertEqual(result["expense"], [0] * 11 + [25])
        self.assertEqual(result["netflow"], [100] + [0] * 10 + [-25])


if __name__ == "__main__":
    unittest.main()