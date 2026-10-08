import os
import unittest
from datetime import datetime
from unittest.mock import patch

from sqlalchemy import inspect

from application import create_app
from application.extensions import db
from application.models import TransactionHistory


class TestAppInitialization(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-only-secret",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )

        self.context = self.app.app_context()
        self.context.push()

        self.runner = self.app.test_cli_runner()

    def tearDown(self):
        try:
            db.session.remove()
            db.drop_all()
        finally:
            self.context.pop()

    def test_missing_secret_key_prevents_app_creation(self):
        with patch.dict(os.environ, {"SECRET_KEY": ""}):
            with self.assertRaisesRegex(
                RuntimeError,
                "SECRET_KEY",
            ):
                create_app()

    def test_explicit_secret_key_overrides_missing_environment_value(self):
        with patch.dict(os.environ, {"SECRET_KEY": ""}):
            app = create_app(
                {
                    "TESTING": True,
                    "SECRET_KEY": "explicit-test-secret",
                    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                }
            )

        self.assertEqual(
            app.config["SECRET_KEY"],
            "explicit-test-secret",
        )

    def test_init_db_creates_transaction_table(self):
        table_name = TransactionHistory.__tablename__

        self.assertNotIn(
            table_name,
            inspect(db.engine).get_table_names(),
        )

        result = self.runner.invoke(args=["init-db"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Database tables created.", result.output)
        self.assertIn(
            table_name,
            inspect(db.engine).get_table_names(),
        )
        self.assertEqual(TransactionHistory.query.count(), 0)

    def test_repeating_init_db_preserves_existing_transactions(self):
        first_run = self.runner.invoke(args=["init-db"])
        self.assertEqual(first_run.exit_code, 0, first_run.output)

        entry = TransactionHistory(
            type="Income",
            first_category="Work",
            second_category="Salary",
            date=datetime(2024, 3, 15),
            amount_cents=1250,
        )
        db.session.add(entry)
        db.session.commit()

        entry_id = entry.id

        second_run = self.runner.invoke(args=["init-db"])

        self.assertEqual(second_run.exit_code, 0, second_run.output)
        self.assertEqual(TransactionHistory.query.count(), 1)

        db.session.expire_all()
        saved_entry = db.session.get(TransactionHistory, entry_id)

        self.assertIsNotNone(saved_entry)
        self.assertEqual(saved_entry.amount_cents, 1250)


if __name__ == "__main__":
    unittest.main()
