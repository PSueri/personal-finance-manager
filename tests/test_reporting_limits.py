from datetime import date, datetime

from application.extensions import db
from application.models import TransactionHistory
from application.money import MAX_AMOUNT_CENTS
from application.reporting import get_category_totals, get_monthly_cashflow
from tests.base import DatabaseTestCase


class TestReportingLimits(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.reference_date = date.today()
        transaction_date = datetime(
            self.reference_date.year,
            self.reference_date.month,
            1,
        )

        for transaction_type, amount in [
            ("Income", MAX_AMOUNT_CENTS),
            ("Income", 1),
            ("Expense", MAX_AMOUNT_CENTS),
            ("Expense", 2),
        ]:
            is_income = transaction_type == "Income"

            db.session.add(
                TransactionHistory(
                    type=transaction_type,
                    first_category="Work" if is_income else "Food",
                    second_category="Salary" if is_income else "Grocery",
                    date=transaction_date,
                    amount_cents=amount,
                )
            )

        db.session.commit()

    def test_monthly_cashflow_exceeds_sqlite_integer_limit_exactly(self):
        result = get_monthly_cashflow(self.reference_date)

        self.assertEqual(
            result["income"],
            [0] * 11 + [MAX_AMOUNT_CENTS + 1],
        )
        self.assertEqual(
            result["expense"],
            [0] * 11 + [MAX_AMOUNT_CENTS + 2],
        )
        self.assertEqual(result["netflow"], [0] * 11 + [-1])

    def test_category_totals_exceed_sqlite_integer_limit_exactly(self):
        for month in [self.reference_date.month, None]:
            with self.subTest(month=month):
                result = get_category_totals(
                    self.reference_date.year,
                    month,
                )

                self.assertEqual(
                    result["income"],
                    {
                        "labels": ["Salary"],
                        "amounts": [MAX_AMOUNT_CENTS + 1],
                    },
                )
                self.assertEqual(
                    result["expense"],
                    {
                        "labels": ["Food"],
                        "amounts": [MAX_AMOUNT_CENTS + 2],
                    },
                )

    def test_dashboard_handles_totals_above_sqlite_integer_limit(self):
        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 200)
