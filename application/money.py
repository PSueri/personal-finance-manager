import re

MAX_AMOUNT_CENTS = 9_223_372_036_854_775_807


def parse_amount_to_cents(amount_text):
    """Convert a positive amount with up to two decimal places to cents."""
    normalized = amount_text.strip()

    if not re.fullmatch(r"[0-9]+(?:[.,][0-9]{1,2})?", normalized):
        raise ValueError("Enter a valid amount with at most two decimal places.")

    normalized = normalized.replace(",", ".")
    whole_part, _, decimal_part = normalized.partition(".")

    cents = int(whole_part) * 100 + int(decimal_part.ljust(2, "0") or "0")

    if cents <= 0:
        raise ValueError("The amount must be greater than zero.")
    if cents > MAX_AMOUNT_CENTS:
        raise ValueError("The amount exceeds the supported maximum.")

    return cents


def format_cents(amount_cents):
    """Format integer cents using two decimal places and a decimal comma."""
    sign = "-" if amount_cents < 0 else ""
    euros, cents = divmod(abs(amount_cents), 100)

    return f"{sign}{euros},{cents:02d}"
