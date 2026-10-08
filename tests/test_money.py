import unittest

from application.money import MAX_AMOUNT_CENTS, format_cents, parse_amount_to_cents


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

    def test_maximum_supported_amount_is_accepted(self):
        self.assertEqual(
            parse_amount_to_cents("92233720368547758.07"),
            MAX_AMOUNT_CENTS,
        )

    def test_amounts_above_the_supported_maximum_are_rejected(self):
        for amount in [
            "92233720368547758.08",
            "99999999999999999999",
        ]:
            with self.subTest(amount=amount):
                with self.assertRaisesRegex(
                    ValueError,
                    "exceeds the supported maximum",
                ):
                    parse_amount_to_cents(amount)

class TestAmountFormatting(unittest.TestCase):
    def test_non_negative_amounts_are_formatted_with_two_decimal_places(self):
        cases = [
            (0, "0,00"),
            (1, "0,01"),
            (10, "0,10"),
            (100, "1,00"),
            (1250, "12,50"),
            (10000, "100,00"),
        ]

        for cents, expected in cases:
            with self.subTest(cents=cents):
                self.assertEqual(format_cents(cents), expected)

    def test_negative_amounts_preserve_the_sign(self):
        cases = [
            (-1, "-0,01"),
            (-1250, "-12,50"),
        ]

        for cents, expected in cases:
            with self.subTest(cents=cents):
                self.assertEqual(format_cents(cents), expected)

if __name__ == "__main__":
    unittest.main()