from datetime import date


def get_last_twelve_month_labels(reference_date=None):
    """Return 12-month labels ending with the reference month."""
    if reference_date is None:
        reference_date = date.today()

    current_month_index = (
        reference_date.year * 12 + reference_date.month - 1
    )

    labels = []

    for offset in range(-11, 1):
        month_index = current_month_index + offset
        year, zero_based_month = divmod(month_index, 12)

        month_start = date(year, zero_based_month + 1, 1)
        labels.append(month_start.strftime("%Y %b"))

    return labels