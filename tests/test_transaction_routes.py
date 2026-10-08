import unittest
import json
import re
from datetime import datetime
from html.parser import HTMLParser

from application.extensions import db
from application.models import TransactionHistory
from tests.base import DatabaseTestCase



class CSRFTokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "input" and attributes.get("name") == "csrf_token":
            self.token = attributes.get("value")


class TestTransactionRoutes(DatabaseTestCase):

    def get_csrf_token(self):
        response = self.client.get("/add")
        self.assertEqual(response.status_code, 200)

        parser = CSRFTokenParser()
        parser.feed(response.get_data(as_text=True))

        self.assertIsNotNone(parser.token)
        return parser.token

    def transaction_data(self, **changes):
        data = {
            "type": "Income",
            "first_category": "Work",
            "second_category": "Salary",
            "date": "2024-03-15",
            "amount": "100",
        }
        data.update(changes)
        return data

    def create_transaction(self):
        entry = TransactionHistory(
            type="Income",
            first_category="Work",
            second_category="Salary",
            date=datetime(2024, 3, 15),
            amount_cents=100,
        )

        db.session.add(entry)
        db.session.commit()

        return entry.id

    def test_valid_submission_saves_transaction_and_redirects(self):
        response = self.client.post(
            "/add",
            data=self.transaction_data(
                csrf_token=self.get_csrf_token()
            ),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/transactions"))
        self.assertEqual(TransactionHistory.query.count(), 1)

        entry = TransactionHistory.query.one()
        self.assertEqual(entry.type, "Income")
        self.assertEqual(entry.first_category, "Work")
        self.assertEqual(entry.second_category, "Salary")
        self.assertEqual(entry.amount_cents, 10000)
        self.assertEqual(entry.date, datetime(2024, 3, 15))

    def test_inconsistent_categories_do_not_save_transaction(self):
        response = self.client.post(
            "/add",
            data=self.transaction_data(
                csrf_token=self.get_csrf_token(),
                first_category="Food",
                second_category="Grocery",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TransactionHistory.query.count(), 0)
        self.assertIn(
            "The category does not belong to the selected transaction type.",
            response.get_data(as_text=True),
        )

    def test_submission_without_csrf_token_is_rejected(self):
        response = self.client.post(
            "/add",
            data=self.transaction_data(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TransactionHistory.query.count(), 0)

    def test_submission_with_invalid_csrf_token_is_rejected(self):
        self.get_csrf_token()

        response = self.client.post(
            "/add",
            data=self.transaction_data(csrf_token="invalid-token"),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TransactionHistory.query.count(), 0)

    def test_get_request_cannot_delete_transaction(self):
        entry_id = self.create_transaction()

        response = self.client.get(f"/delete/{entry_id}")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(TransactionHistory.query.count(), 1)

    def test_deletion_without_csrf_token_is_rejected(self):
        entry_id = self.create_transaction()

        response = self.client.post(f"/delete/{entry_id}")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TransactionHistory.query.count(), 1)

    def test_valid_deletion_removes_transaction_and_redirects(self):
        entry_id = self.create_transaction()

        response = self.client.post(
            f"/delete/{entry_id}",
            data={"csrf_token": self.get_csrf_token()},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/transactions"))
        self.assertEqual(TransactionHistory.query.count(), 0)

    def test_deleting_unknown_transaction_returns_not_found(self):
        response = self.client.post(
            "/delete/999",
            data={"csrf_token": self.get_csrf_token()},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(TransactionHistory.query.count(), 0)

    def test_decimal_amounts_are_saved_in_cents(self):
        cases = [
            ("12.50", 1250, "12,50"),
            ("12,50", 1250, "12,50"),
            ("0.01", 1, "0,01"),
        ]

        for count, (text, expected_cents, displayed_amount) in enumerate(
            cases,
            start=1,
        ):
            with self.subTest(amount=text):
                response = self.client.post(
                    "/add",
                    data=self.transaction_data(
                        amount=text,
                        csrf_token=self.get_csrf_token(),
                    ),
                )

                self.assertEqual(response.status_code, 302)
                self.assertEqual(TransactionHistory.query.count(), count)

                entry = (
                    TransactionHistory.query
                    .order_by(TransactionHistory.id.desc())
                    .first()
                )

                self.assertEqual(entry.amount_cents, expected_cents)

                history = self.client.get("/transactions")

                self.assertEqual(history.status_code, 200)
                self.assertIn(
                    f"{displayed_amount} €",
                    history.get_data(as_text=True),
                )

    def test_amount_with_three_decimal_places_is_not_saved(self):
        response = self.client.post(
            "/add",
            data=self.transaction_data(
                amount="12.345",
                csrf_token=self.get_csrf_token(),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TransactionHistory.query.count(), 0)
        self.assertIn(
            "Enter a valid amount with at most two decimal places.",
            response.get_data(as_text=True),
        )

    def test_dashboard_chart_values_are_in_euros(self):
        transaction_date = datetime.today()

        db.session.add_all([
            TransactionHistory(
                type="Income",
                first_category="Work",
                second_category="Salary",
                amount_cents=2000,
                date=transaction_date,
            ),
            TransactionHistory(
                type="Expense",
                first_category="Food",
                second_category="Grocery",
                amount_cents=1250,
                date=transaction_date,
            ),
        ])
        db.session.commit()

        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 200)

        match = re.search(
            r'<script\b[^>]*id="dashboard-data"[^>]*>(.*?)</script>',
            response.get_data(as_text=True),
            re.DOTALL,
        )
        self.assertIsNotNone(match, "Dashboard JSON data is missing.")

        data = json.loads(match.group(1))

        self.assertEqual(data["income_month"][-1], 20)
        self.assertEqual(data["expense_month"][-1], 12.5)
        self.assertEqual(data["netflow_month"][-1], 7.5)

        self.assertEqual(data["category_incomes_values"], [20])
        self.assertEqual(data["category_expenses_values"], [12.5])
        self.assertEqual(data["category_incomes_year_values"], [20])
        self.assertEqual(data["category_expenses_year_values"], [12.5])


if __name__ == "__main__":
    unittest.main()