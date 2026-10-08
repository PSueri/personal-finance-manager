import unittest
from datetime import date

from application.reporting import get_last_twelve_month_labels


class TestLastTwelveMonthLabels(unittest.TestCase):
    def test_leap_year_returns_the_expected_twelve_months(self):
        expected_months = [
            date(2023, 4, 1),
            date(2023, 5, 1),
            date(2023, 6, 1),
            date(2023, 7, 1),
            date(2023, 8, 1),
            date(2023, 9, 1),
            date(2023, 10, 1),
            date(2023, 11, 1),
            date(2023, 12, 1),
            date(2024, 1, 1),
            date(2024, 2, 1),
            date(2024, 3, 1),
        ]

        labels = get_last_twelve_month_labels(date(2024, 3, 31))

        self.assertEqual(
            labels,
            [month.strftime("%Y %b") for month in expected_months],
        )

    def test_january_range_crosses_the_year_boundary(self):
        labels = get_last_twelve_month_labels(date(2026, 1, 15))

        self.assertEqual(len(labels), 12)
        self.assertEqual(
            labels[0],
            date(2025, 2, 1).strftime("%Y %b"),
        )
        self.assertEqual(
            labels[-1],
            date(2026, 1, 1).strftime("%Y %b"),
        )
        self.assertEqual(len(set(labels)), 12)

    def test_day_of_month_does_not_change_the_range(self):
        first_day = get_last_twelve_month_labels(date(2024, 3, 1))
        last_day = get_last_twelve_month_labels(date(2024, 3, 31))

        self.assertEqual(first_day, last_day)


if __name__ == "__main__":
    unittest.main()
