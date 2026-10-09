from datetime import date, datetime

from application import create_app
from application.extensions import db
from application.models import TransactionHistory


DEMO_DATABASE_URI = "sqlite:///screenshots_demo.db"


def main():
    app = create_app(
        {
            "SQLALCHEMY_DATABASE_URI": DEMO_DATABASE_URI,
        }
    )

    with app.app_context():
        existing_id = db.session.scalar(db.select(TransactionHistory.id).limit(1))

        if existing_id is not None:
            print("The demo database already contains transactions. No data added.")
            return

        today = date.today()
        current_month_index = today.year * 12 + today.month - 1
        entries = []

        for index in range(12):
            month_index = current_month_index - 11 + index
            year, zero_based_month = divmod(month_index, 12)
            month = zero_based_month + 1

            monthly_transactions = [
                ("Income", "Work", "Salary", 200_000 + index * 2_500),
                ("Income", "OtherIncome", "Gift", 7_500 + index % 3 * 2_500),
                ("Expense", "Home", "Rent", 75_000),
                ("Expense", "Home", "Grocery", 25_000 + index % 4 * 1_500),
                ("Expense", "Bills", "Light", 8_500 + index % 3 * 2_000),
                ("Expense", "Food", "Restourant", 6_000 + index * 300),
                ("Expense", "Transportation", "PublicTransport", 4_500),
                ("Expense", "Shopping", "Clothes", 6_500 + index % 4 * 1_000),
            ]

            # Include one month with negative net cash flow.
            if index == 8:
                monthly_transactions.append(("Expense", "Holiday", "Generic", 250_000))

            for position, transaction in enumerate(
                monthly_transactions,
                start=1,
            ):
                transaction_type, category, subcategory, amount = transaction

                day = position
                if (year, month) == (today.year, today.month):
                    day = min(day, today.day)

                entries.append(
                    TransactionHistory(
                        type=transaction_type,
                        first_category=category,
                        second_category=subcategory,
                        date=datetime(year, month, day),
                        amount_cents=amount,
                    )
                )

        db.session.add_all(entries)
        db.session.commit()

        print(f"Created {len(entries)} demo transactions.")
        print("Database: instance/screenshots_demo.db")


if __name__ == "__main__":
    main()
