import calendar
import unittest
from datetime import datetime

from application.forms import SelectYearMonthForm
from tests.base import DatabaseTestCase


class TestDashboardPeriod(DatabaseTestCase):
    APP_CONFIG = {
        "WTF_CSRF_ENABLED": False,
    }

    def validate_form(self, **changes):
        today = datetime.today()

        data = {
            "selected_year": str(today.year),
            "selected_month": str(today.month),
        }
        data.update(changes)

        with self.app.test_request_context(
            "/dashboard",
            method="POST",
            data=data,
        ):
            form = SelectYearMonthForm()
            is_valid = form.validate_on_submit()

        return form, is_valid

    def test_form_defaults_to_current_period(self):
        today = datetime.today()

        with self.app.test_request_context("/dashboard"):
            form = SelectYearMonthForm()

            self.assertEqual(form.selected_year.data, today.year)
            self.assertEqual(form.selected_month.data, today.month)

    def test_valid_form_produces_integer_values(self):
        form, is_valid = self.validate_form(selected_month="2")

        self.assertTrue(is_valid, form.errors)
        self.assertIsInstance(form.selected_year.data, int)
        self.assertIsInstance(form.selected_month.data, int)
        self.assertEqual(form.selected_month.data, 2)

    def test_invalid_months_are_rejected(self):
        for month in ["0", "13", "abc"]:
            with self.subTest(month=month):
                form, is_valid = self.validate_form(
                    selected_month=month
                )

                self.assertFalse(is_valid)
                self.assertIn("selected_month", form.errors)

    def test_unavailable_years_are_rejected(self):
        unavailable_year = str(datetime.today().year - 10)

        for year in ["0", unavailable_year, "abc"]:
            with self.subTest(year=year):
                form, is_valid = self.validate_form(
                    selected_year=year
                )

                self.assertFalse(is_valid)
                self.assertIn("selected_year", form.errors)

    def test_dashboard_get_shows_current_period(self):
        today = datetime.today()
        expected_period = (
            f"{today.year}, {calendar.month_name[today.month]}"
        )

        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            expected_period,
            response.get_data(as_text=True),
        )

    def test_valid_post_shows_selected_period(self):
        selected_year = datetime.today().year - 1
        selected_month = 2
        expected_period = (
            f"{selected_year}, {calendar.month_name[selected_month]}"
        )

        response = self.client.post(
            "/dashboard",
            data={
                "selected_year": str(selected_year),
                "selected_month": str(selected_month),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            expected_period,
            response.get_data(as_text=True),
        )

    def test_invalid_post_shows_error_and_current_period(self):
        today = datetime.today()
        expected_period = (
            f"{today.year}, {calendar.month_name[today.month]}"
        )

        response = self.client.post(
            "/dashboard",
            data={
                "selected_year": str(today.year),
                "selected_month": "0",
            },
        )

        self.assertEqual(response.status_code, 400)

        html = response.get_data(as_text=True)

        self.assertIn("The selected period is invalid.", html)
        self.assertIn(expected_period, html)


if __name__ == "__main__":
    unittest.main()