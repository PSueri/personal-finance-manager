from flask import Blueprint, abort, render_template, flash, redirect, url_for, get_flashed_messages, request
from application.extensions import db
from application.forms import UserInputForm, SelectYearMonthForm
from application.models import TransactionHistory
import requests
import calendar
from datetime import datetime

from application.categories import CATEGORY_TREE
from application.reporting import get_category_totals, get_monthly_cashflow


main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template('index.html', title='Home')

@main_bp.route("/add", methods=["GET", "POST"])
def add_transaction():
    form = UserInputForm()
    if form.validate_on_submit():
        entry=TransactionHistory(type=form.type.data,
                                 first_category=form.first_category.data,
                                 second_category=form.second_category.data,
                                 amount=form.amount.data,
                                 date=form.date.data)
        db.session.add(entry)
        db.session.commit()
        flash("Successful entry", 'success')
        return redirect(url_for('main.show_transactions'))
    return render_template(
        "add.html",
        title="Add",
        form=form,
        category_tree=CATEGORY_TREE,
    )

@main_bp.route("/transactions")
def show_transactions():
    entries=TransactionHistory.query.order_by(TransactionHistory.date.desc()).all()
    return render_template('show_transactions.html', title='Transactions', entries=entries)

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
        income_month=cashflow["income"],
        expense_month=cashflow["expense"],
        netflow_month=cashflow["netflow"],
        dates_label=cashflow["labels"],
        cat_exp_amount=monthly_categories["expense"]["amounts"],
        cat_exp_label=monthly_categories["expense"]["labels"],
        cat_exp_amount_year=yearly_categories["expense"]["amounts"],
        cat_exp_label_year=yearly_categories["expense"]["labels"],
        cat_inc_amount=monthly_categories["income"]["amounts"],
        cat_inc_label=monthly_categories["income"]["labels"],
        cat_inc_amount_year=yearly_categories["income"]["amounts"],
        cat_inc_label_year=yearly_categories["income"]["labels"],
        selectionform=selectionform,
        current_period=current_period,
    ), status_code

@main_bp.route("/delete/<int:entry_id>", methods=["POST"])
def delete(entry_id):
    entry = db.session.get(TransactionHistory, entry_id)

    if entry is None:
        abort(404)

    db.session.delete(entry)
    db.session.commit()

    flash("Successful Deletion", "success")
    return redirect(url_for("main.show_transactions"))