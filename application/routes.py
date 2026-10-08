from flask import Blueprint, abort, render_template, flash, redirect, url_for, get_flashed_messages, request, current_app
from sqlalchemy.exc import SQLAlchemyError
from application.extensions import db
from application.forms import UserInputForm, SelectYearMonthForm
from application.models import TransactionHistory
from application.money import parse_amount_to_cents
import requests
import calendar
from datetime import datetime

from application.categories import CATEGORY_TREE
from application.reporting import get_category_totals, get_monthly_cashflow

def chart_amounts(amounts_cents):
    return [amount / 100 for amount in amounts_cents]

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template('index.html', title='Home')

@main_bp.route("/add", methods=["GET", "POST"])
def add_transaction():
    form = UserInputForm()
    status_code = 200

    if form.validate_on_submit():
        entry = TransactionHistory(
            type=form.type.data,
            first_category=form.first_category.data,
            second_category=form.second_category.data,
            amount_cents=parse_amount_to_cents(form.amount.data),
            date=form.date.data,
        )

        try:
            db.session.add(entry)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to save transaction."
            )

            flash(
                "The transaction could not be saved. Please try again.",
                "danger",
            )
            status_code = 503
        else:
            flash("Successful entry", "success")
            return redirect(url_for("main.show_transactions"))

    return render_template(
        "add.html",
        title="Add",
        form=form,
        category_tree=CATEGORY_TREE,
    ), status_code

@main_bp.route("/transactions")
def show_transactions():
    page = request.args.get("page", default=1, type=int)

    pagination = db.paginate(
        db.select(TransactionHistory).order_by(
            TransactionHistory.date.desc(),
            TransactionHistory.id.desc(),
        ),
        page=page,
        per_page=20,
        max_per_page=20,
        error_out=True,
    )

    return render_template(
        "show_transactions.html",
        title="Transactions",
        entries=pagination.items,
        pagination=pagination,
    )

@main_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    selectionform = SelectYearMonthForm()
    today = datetime.now()

    year = today.year
    month = today.month
    status_code = 200

    if request.method == "POST":
        if selectionform.validate_on_submit():
            year = selectionform.selected_year.data
            month = selectionform.selected_month.data
        else:
            status_code = 400

    current_period = f"{year}, {calendar.month_name[month]}"

    cashflow = get_monthly_cashflow()
    monthly_categories = get_category_totals(year, month)
    yearly_categories = get_category_totals(year)

    return render_template(
        "dashboard.html",
        title="Dashboard",
        income_month=chart_amounts(cashflow["income"]),
        expense_month=chart_amounts(cashflow["expense"]),
        netflow_month=chart_amounts(cashflow["netflow"]),
        dates_label=cashflow["labels"],
        cat_exp_amount=chart_amounts(monthly_categories["expense"]["amounts"]),
        cat_exp_label=monthly_categories["expense"]["labels"],
        cat_exp_amount_year=chart_amounts(yearly_categories["expense"]["amounts"]),
        cat_exp_label_year=yearly_categories["expense"]["labels"],
        cat_inc_amount=chart_amounts(monthly_categories["income"]["amounts"]),
        cat_inc_label=monthly_categories["income"]["labels"],
        cat_inc_amount_year=chart_amounts(yearly_categories["income"]["amounts"]),
        cat_inc_label_year=yearly_categories["income"]["labels"],
        selectionform=selectionform,
        current_period=current_period,
    ), status_code

@main_bp.route("/delete/<int:entry_id>", methods=["POST"])
def delete(entry_id):
    entry = db.session.get(TransactionHistory, entry_id)

    if entry is None:
        abort(404)

    try:
        db.session.delete(entry)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()

        current_app.logger.exception(
            "Failed to delete transaction."
        )

        flash(
            "The transaction could not be deleted. Please try again.",
            "danger",
        )
    else:
        flash("Successful Deletion", "success")

    return redirect(url_for("main.show_transactions"))