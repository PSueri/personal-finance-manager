import unittest

from application import create_app
from application.forms import UserInputForm


class TestTransactionForm(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        })

    def validate_form(self, **changes):
        data = {
            "type": "Income",
            "first_category": "Work",
            "second_category": "Salary",
            "date": "2024-03-15",
            "amount": "100",
        }
        data.update(changes)

        with self.app.test_request_context(
            "/add",
            method="POST",
            data=data,
        ):
            form = UserInputForm()
            is_valid = form.validate_on_submit()

        return form, is_valid

    def test_valid_transaction_is_accepted(self):
        form, is_valid = self.validate_form()

        self.assertTrue(is_valid, form.errors)

    def test_required_fields_cannot_be_empty(self):
        fields = [
            "type",
            "first_category",
            "second_category",
            "date",
            "amount",
        ]

        for field_name in fields:
            with self.subTest(field=field_name):
                form, is_valid = self.validate_form(
                    **{field_name: ""}
                )

                self.assertFalse(is_valid)
                self.assertIn(field_name, form.errors)

    def test_invalid_amounts_are_rejected(self):
        for amount in ["0", "-10", "abc"]:
            with self.subTest(amount=amount):
                form, is_valid = self.validate_form(amount=amount)

                self.assertFalse(is_valid)
                self.assertIn("amount", form.errors)

    def test_category_must_belong_to_transaction_type(self):
        form, is_valid = self.validate_form(
            type="Income",
            first_category="Food",
            second_category="Grocery",
        )

        self.assertFalse(is_valid)
        self.assertIn("first_category", form.errors)

    def test_subcategory_must_belong_to_category(self):
        form, is_valid = self.validate_form(
            type="Income",
            first_category="Work",
            second_category="Grocery",
        )

        self.assertFalse(is_valid)
        self.assertIn("second_category", form.errors)


if __name__ == "__main__":
    unittest.main()