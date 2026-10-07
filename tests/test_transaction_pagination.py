import re
import unittest
from datetime import datetime

from application import create_app
from application.extensions import db
from application.models import TransactionHistory


class TestTransactionPagination(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        })

        self.context = self.app.app_context()
        self.context.push()

        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        try:
            db.session.remove()
            db.drop_all()
        finally:
            self.context.pop()

    def create_transactions(self, count):
        entries = [
            TransactionHistory(
                type="Income",
                first_category="Work",
                second_category="Salary",
                amount=100,
                date=datetime(2024, 3, 15),
            )
            for _ in range(count)
        ]

        db.session.add_all(entries)
        db.session.commit()

        return [entry.id for entry in entries]

    def visible_transaction_ids(self, response):
        html = response.get_data(as_text=True)

        return [
            int(entry_id)
            for entry_id in re.findall(
                r'action="/delete/(\d+)"',
                html,
            )
        ]

    def test_empty_history_returns_success(self):
        response = self.client.get("/transactions")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.visible_transaction_ids(response), [])
        self.assertIn(
            "No transactions yet.",
            response.get_data(as_text=True),
        )

    def test_first_page_contains_twenty_transactions(self):
        ids = self.create_transactions(25)

        response = self.client.get("/transactions")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.visible_transaction_ids(response),
            list(reversed(ids))[:20],
        )

    def test_second_page_contains_remaining_transactions(self):
        ids = self.create_transactions(25)

        response = self.client.get("/transactions?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.visible_transaction_ids(response),
            list(reversed(ids))[20:],
        )

    def test_date_takes_priority_over_id_when_sorting(self):
        ids = self.create_transactions(3)

        first_entry = db.session.get(TransactionHistory, ids[0])
        first_entry.date = datetime(2024, 3, 20)
        db.session.commit()

        response = self.client.get("/transactions")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.visible_transaction_ids(response),
            [ids[0], ids[2], ids[1]],
        )

    def test_invalid_page_returns_not_found(self):
        self.create_transactions(25)

        for page in [0, -1, 3]:
            with self.subTest(page=page):
                response = self.client.get(
                    f"/transactions?page={page}"
                )

                self.assertEqual(response.status_code, 404)

    def test_page_size_cannot_be_increased_through_query_string(self):
        ids = self.create_transactions(25)

        response = self.client.get(
            "/transactions?per_page=1000"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.visible_transaction_ids(response),
            list(reversed(ids))[:20],
        )


if __name__ == "__main__":
    unittest.main()