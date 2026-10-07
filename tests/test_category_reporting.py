import unittest
from datetime import datetime

from application.extensions import db
from application.models import TransactionHistory
from application.reporting import get_category_totals
from tests.base import DatabaseTestCase


class TestCategoryReporting(DatabaseTestCase):

    def add_transaction(
        self,
        transaction_type,
        category,
        subcategory,
        amount,
        transaction_date,
    ):
        db.session.add(TransactionHistory(
            type=transaction_type,
            first_category=category,
            second_category=subcategory,
            amount=amount,
            date=transaction_date,
        ))

    def test_empty_period_returns_empty_lists(self):
        expected = {
            "income": {"labels": [], "amounts": []},
            "expense": {"labels": [], "amounts": []},
        }

        self.assertEqual(get_category_totals(2024, 3), expected)
        self.assertEqual(get_category_totals(2024), expected)

    def test_monthly_totals_use_the_correct_category_level(self):
        transactions = [
            ("Income", "Work", "Salary", 1000, datetime(2024, 3, 1)),
            ("Income", "Work", "Salary", 200, datetime(2024, 3, 15)),
            ("Income", "Work", "Bonus", 50, datetime(2024, 3, 20)),
            ("Expense", "Food", "Grocery", 20, datetime(2024, 3, 2)),
            ("Expense", "Food", "Bar", 10, datetime(2024, 3, 3)),
            ("Expense", "Home", "Rent", 500, datetime(2024, 3, 4)),
            ("Income", "Work", "Salary", 9000, datetime(2024, 2, 29)),
            ("Expense", "Home", "Rent", 8000, datetime(2024, 4, 1)),
        ]

        for transaction in transactions:
            self.add_transaction(*transaction)

        db.session.commit()

        result = get_category_totals(2024, 3)

        self.assertEqual(result["income"], {
            "labels": ["Bonus", "Salary"],
            "amounts": [50, 1200],
        })
        self.assertEqual(result["expense"], {
            "labels": ["Food", "Home"],
            "amounts": [30, 500],
        })

    def test_yearly_totals_include_only_the_selected_year(self):
        transactions = [
            (
                "Income", "Work", "Salary", 9000,
                datetime(2023, 12, 31, 23, 59, 59),
            ),
            (
                "Income", "Work", "Salary", 100,
                datetime(2024, 1, 1),
            ),
            (
                "Income", "Work", "Salary", 50,
                datetime(2024, 7, 15),
            ),
            (
                "Expense", "Food", "Grocery", 25,
                datetime(2024, 12, 31, 23, 59, 59),
            ),
            (
                "Expense", "Food", "Grocery", 8000,
                datetime(2025, 1, 1),
            ),
        ]

        for transaction in transactions:
            self.add_transaction(*transaction)

        db.session.commit()

        result = get_category_totals(2024)

        self.assertEqual(result["income"], {
            "labels": ["Salary"],
            "amounts": [150],
        })
        self.assertEqual(result["expense"], {
            "labels": ["Food"],
            "amounts": [25],
        })

        december = get_category_totals(2024, 12)

        self.assertEqual(december["income"], {
            "labels": [],
            "amounts": [],
        })
        self.assertEqual(december["expense"], {
            "labels": ["Food"],
            "amounts": [25],
        })

    def test_invalid_month_is_rejected(self):
        for month in [0, -1, 13]:
            with self.subTest(month=month):
                with self.assertRaises(ValueError):
                    get_category_totals(2024, month)


if __name__ == "__main__":
    unittest.main()