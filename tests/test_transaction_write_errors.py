import unittest
from datetime import datetime
from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from application.extensions import db
from application.models import TransactionHistory
from tests.base import DatabaseTestCase


class TestTransactionWriteErrors(DatabaseTestCase):
    APP_CONFIG = {
        "WTF_CSRF_ENABLED": False,
    }

    def transaction_data(self):
        return {
            "type": "Income",
            "first_category": "Work",
            "second_category": "Salary",
            "date": "2024-03-15",
            "amount": "100",
        }

    def create_transaction(self):
        entry = TransactionHistory(
            type="Income",
            first_category="Work",
            second_category="Salary",
            date=datetime(2024, 3, 15),
            amount=100,
        )

        db.session.add(entry)
        db.session.commit()

        return entry.id

    def test_failed_insert_rolls_back_and_allows_retry(self):
        with (
            patch.object(
                db.session,
                "commit",
                side_effect=SQLAlchemyError("Simulated commit failure"),
            ),
            patch.object(
                db.session,
                "rollback",
                wraps=db.session.rollback,
            ) as rollback,
            patch.object(
                self.app.logger,
                "exception",
            ) as log_exception,
        ):
            response = self.client.post(
                "/add",
                data=self.transaction_data(),
            )

            self.assertEqual(response.status_code, 503)
            rollback.assert_called_once()
            log_exception.assert_called_once()

        html = response.get_data(as_text=True)

        self.assertIn(
            "The transaction could not be saved. Please try again.",
            html,
        )
        self.assertNotIn("Successful entry", html)
        self.assertEqual(TransactionHistory.query.count(), 0)

        retry = self.client.post(
            "/add",
            data=self.transaction_data(),
        )

        self.assertEqual(retry.status_code, 302)
        self.assertEqual(TransactionHistory.query.count(), 1)

    def test_failed_deletion_rolls_back_and_allows_retry(self):
        entry_id = self.create_transaction()

        with (
            patch.object(
                db.session,
                "commit",
                side_effect=SQLAlchemyError("Simulated commit failure"),
            ),
            patch.object(
                db.session,
                "rollback",
                wraps=db.session.rollback,
            ) as rollback,
            patch.object(
                self.app.logger,
                "exception",
            ) as log_exception,
        ):
            response = self.client.post(
                f"/delete/{entry_id}",
                follow_redirects=True,
            )

            self.assertEqual(response.status_code, 200)
            rollback.assert_called_once()
            log_exception.assert_called_once()

        html = response.get_data(as_text=True)

        self.assertIn(
            "The transaction could not be deleted. Please try again.",
            html,
        )
        self.assertNotIn("Successful Deletion", html)
        self.assertEqual(TransactionHistory.query.count(), 1)
        self.assertIsNotNone(
            db.session.get(TransactionHistory, entry_id)
        )

        retry = self.client.post(f"/delete/{entry_id}")

        self.assertEqual(retry.status_code, 302)
        self.assertEqual(TransactionHistory.query.count(), 0)


if __name__ == "__main__":
    unittest.main()