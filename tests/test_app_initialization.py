import os
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from sqlalchemy import inspect

from application import create_app
from application.extensions import db
from application.models import TransactionHistory


MIGRATIONS_DIRECTORY = Path(__file__).resolve().parents[1] / "migrations"
INITIAL_REVISION = "47a4346290ab"


class TestAppInitialization(unittest.TestCase):
    def setUp(self):
        self.temp_directory = TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        database_path = Path(self.temp_directory.name) / "test.db"

        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-only-secret",
                "SQLALCHEMY_DATABASE_URI": (f"sqlite:///{database_path.as_posix()}"),
            }
        )

        self.context = self.app.app_context()
        self.context.push()

        self.addCleanup(self.context.pop)
        self.addCleanup(db.engine.dispose)
        self.addCleanup(db.session.remove)

        self.runner = self.app.test_cli_runner()

    def run_db_command(self, command, *arguments):
        result = self.runner.invoke(
            args=[
                "db",
                command,
                "--directory",
                str(MIGRATIONS_DIRECTORY),
                *arguments,
            ]
        )

        self.assertEqual(
            result.exit_code,
            0,
            f"{result.output}\n{result.exception!r}",
        )

        return result

    def test_missing_secret_key_prevents_app_creation(self):
        with patch.dict(os.environ, {"SECRET_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "SECRET_KEY"):
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

    def test_upgrade_creates_transaction_table(self):
        table_name = TransactionHistory.__tablename__

        self.assertNotIn(
            table_name,
            inspect(db.engine).get_table_names(),
        )

        self.run_db_command("upgrade")

        table_names = inspect(db.engine).get_table_names()

        self.assertIn(table_name, table_names)
        self.assertIn("alembic_version", table_names)
        self.assertEqual(TransactionHistory.query.count(), 0)

    def test_migrated_schema_matches_models(self):
        self.run_db_command("upgrade")
        self.run_db_command("check")

    def test_upgrading_preserves_existing_transactions(self):
        self.run_db_command("upgrade", INITIAL_REVISION)

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
        db.session.remove()

        self.run_db_command("upgrade")
        self.run_db_command("upgrade")

        self.assertEqual(TransactionHistory.query.count(), 1)

        saved_entry = db.session.get(TransactionHistory, entry_id)

        self.assertIsNotNone(saved_entry)
        self.assertEqual(saved_entry.type, "Income")
        self.assertEqual(saved_entry.first_category, "Work")
        self.assertEqual(saved_entry.second_category, "Salary")
        self.assertEqual(saved_entry.date, datetime(2024, 3, 15))
        self.assertEqual(saved_entry.amount_cents, 1250)

    def test_migrations_create_transaction_constraints(self):
        self.run_db_command("upgrade")

        constraints = inspect(db.engine).get_check_constraints(
            TransactionHistory.__tablename__
        )
        constraint_names = {constraint["name"] for constraint in constraints}

        self.assertTrue(
            {
                "ck_transaction_amount_positive",
                "ck_transaction_type_valid",
                "ck_transaction_first_category_required",
                "ck_transaction_second_category_required",
            }.issubset(constraint_names)
        )


if __name__ == "__main__":
    unittest.main()
