from datetime import date, datetime
from application.extensions import db
from application.models import TransactionHistory


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

def get_monthly_cashflow(reference_date=None):
    """Return cash flow for twelve months ending with the reference month."""
    if reference_date is None:
        reference_date = date.today()

    labels = get_last_twelve_month_labels(reference_date)

    current_month_index = (
        reference_date.year * 12 + reference_date.month - 1
    )

    start_year, start_month = divmod(current_month_index - 11, 12)
    end_year, end_month = divmod(current_month_index + 1, 12)

    period_start = datetime(start_year, start_month + 1, 1)
    period_end = datetime(end_year, end_month + 1, 1)

    monthly_totals = {
        label: {"income": 0, "expense": 0}
        for label in labels
    }

    rows = (
        db.session.query(
            TransactionHistory.type,
            TransactionHistory.date,
            db.func.sum(TransactionHistory.amount),
        )
        .filter(
            TransactionHistory.type.in_(["Income", "Expense"]),
            TransactionHistory.date >= period_start,
            TransactionHistory.date < period_end,
        )
        .group_by(
            TransactionHistory.type,
            TransactionHistory.date,
        )
        .all()
    )

    for transaction_type, transaction_date, amount in rows:
        label = transaction_date.strftime("%Y %b")
        key = "income" if transaction_type == "Income" else "expense"

        monthly_totals[label][key] += amount

    income = [
        monthly_totals[label]["income"]
        for label in labels
    ]

    expense = [
        monthly_totals[label]["expense"]
        for label in labels
    ]

    netflow = [
        income_amount - expense_amount
        for income_amount, expense_amount in zip(income, expense)
    ]

    return {
        "labels": labels,
        "income": income,
        "expense": expense,
        "netflow": netflow,
    }

def _query_category_totals(transaction_type, period_start, period_end):
    if transaction_type == "Expense":
        category_column = TransactionHistory.first_category
    else:
        category_column = TransactionHistory.second_category

    rows = (
        db.session.query(
            category_column,
            db.func.sum(TransactionHistory.amount),
        )
        .filter(
            TransactionHistory.type == transaction_type,
            TransactionHistory.date >= period_start,
            TransactionHistory.date < period_end,
        )
        .group_by(category_column)
        .order_by(category_column)
        .all()
    )

    return {
        "labels": [category for category, _ in rows],
        "amounts": [amount for _, amount in rows],
    }


def get_category_totals(year, month=None):
    """Return income and expense totals by category for a month or year."""
    year = int(year)

    if month is None:
        period_start = datetime(year, 1, 1)
        period_end = datetime(year + 1, 1, 1)
    else:
        month = int(month)

        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12.")

        period_start = datetime(year, month, 1)

        next_year, next_month = divmod(year * 12 + month, 12)
        period_end = datetime(next_year, next_month + 1, 1)

    return {
        "income": _query_category_totals("Income", period_start, period_end),
        "expense": _query_category_totals("Expense", period_start, period_end),
    }