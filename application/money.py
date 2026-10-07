import re

def parse_amount_to_cents(amount_text):
    """Convert a positive amount with up to two decimal places to cents."""
    normalized = amount_text.strip()

    if not re.fullmatch(r"[0-9]+(?:[.,][0-9]{1,2})?", normalized):
        raise ValueError(
            "Enter a valid amount with at most two decimal places."
        )

    normalized = normalized.replace(",", ".")
    whole_part, _, decimal_part = normalized.partition(".")

    cents = (
        int(whole_part) * 100
        + int(decimal_part.ljust(2, "0") or "0")
    )

    if cents <= 0:
        raise ValueError("The amount must be greater than zero.")

    return cents