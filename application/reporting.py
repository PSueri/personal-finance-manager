from datetime import date
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
    """Return monthly income, expenses and net cash flow."""
    labels = get_last_twelve_month_labels(reference_date)

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
        .filter(TransactionHistory.type.in_(["Income", "Expense"]))
        .group_by(
            TransactionHistory.type,
            TransactionHistory.date,
        )
        .all()
    )

    for transaction_type, transaction_date, amount in rows:
        label = transaction_date.strftime("%Y %b")

        if label not in monthly_totals:
            continue

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