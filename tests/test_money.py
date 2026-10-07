import unittest

from application.money import parse_amount_to_cents


class TestAmountConversion(unittest.TestCase):
    def test_valid_amounts_are_converted_to_cents(self):
        cases = [
            ("12", 1200),
            ("12.5", 1250),
            ("12.50", 1250),
            ("12,50", 1250),
            ("0.01", 1),
            ("0,10", 10),
            (" 12.50 ", 1250),
        ]

        for text, expected in cases:
            with self.subTest(amount=text):
                self.assertEqual(
                    parse_amount_to_cents(text),
                    expected,
                )

    def test_invalid_amounts_are_rejected(self):
        cases = [
            "",
            " ",
            "0",
            "0.00",
            "-10",
            "abc",
            "12.345",
            "1,234.56",
            "1.234,56",
            "NaN",
            "Infinity",
            "1e3",
        ]

        for text in cases:
            with self.subTest(amount=text):
                with self.assertRaises(ValueError):
                    parse_amount_to_cents(text)


if __name__ == "__main__":
    unittest.main()