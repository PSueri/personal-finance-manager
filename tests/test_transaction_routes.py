import unittest
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


if __name__ == "__main__":
    unittest.main()