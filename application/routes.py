from flask import Blueprint
from application.extensions import db
from flask import render_template, flash, redirect, url_for, get_flashed_messages, request
from application.forms import UserInputForm, SelectYearMonthForm
from application.models import TransactionHistory
import json
import requests
import calendar
from datetime import datetime

from application.categories import CATEGORY_TREE
from application.reporting import get_monthly_cashflow

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

@main_bp.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    # Get selected period
    selectionform = SelectYearMonthForm()
    if selectionform.validate_on_submit():
        year = selectionform.selected_year.data
        selmonth = selectionform.selected_month.data
    else:
        year = 0
        selmonth = 0
    # Set default values if not provided
    if not int(year):
        year = datetime.now().year
    if not int(selmonth):
        selmonth = datetime.now().month

    current_period = str(year)+', '+calendar.month_name[int(selmonth)]

    category_expenses = db.session.query(db.func.sum(TransactionHistory.amount),
                                           TransactionHistory.first_category).filter_by(type='Expense').filter(
                                            db.func.extract('year',TransactionHistory.date) == year).filter(
                                            db.func.extract('month',TransactionHistory.date) == selmonth).group_by(
                                             TransactionHistory.first_category).order_by(
                                             TransactionHistory.first_category).all()
    category_expenses_year = db.session.query(db.func.sum(TransactionHistory.amount),
                                           TransactionHistory.first_category).filter_by(type='Expense').filter(
                                            db.func.extract('year',TransactionHistory.date) == year).group_by(
                                             TransactionHistory.first_category).order_by(
                                             TransactionHistory.first_category).all()
    category_incomes = db.session.query(db.func.sum(TransactionHistory.amount),
                                           TransactionHistory.second_category).filter_by(type='Income').filter(
                                            db.func.extract('year',TransactionHistory.date) == year).filter(
                                            db.func.extract('month',TransactionHistory.date) == selmonth).group_by(
                                            TransactionHistory.second_category).order_by(
                                            TransactionHistory.second_category).all()
    category_incomes_year = db.session.query(db.func.sum(TransactionHistory.amount),
                                           TransactionHistory.second_category).filter_by(type='Income').filter(
                                            db.func.extract('year',TransactionHistory.date) == year).group_by(
                                            TransactionHistory.second_category).order_by(
                                            TransactionHistory.second_category).all()

    # Create lists using list comprehension for monthly and yearly category amounts
    cat_exp_label = [category for _, category in category_expenses]
    cat_exp_amount = [amount for amount, _ in category_expenses]
    cat_exp_label_year = [category for _, category in category_expenses_year]
    cat_exp_amount_year = [amount for amount, _ in category_expenses_year]

    cat_inc_label = [category for _, category in category_incomes]
    cat_inc_amount = [amount for amount, _ in category_incomes]
    cat_inc_label_year = [category for _, category in category_incomes_year]
    cat_inc_amount_year = [amount for amount, _ in category_incomes_year]

    cashflow = get_monthly_cashflow()

    return render_template('dashboard.html', title='Dashboard',
                           income_month=json.dumps(cashflow["income"]),
                           expense_month=json.dumps(cashflow["expense"]),
                           netflow_month=json.dumps(cashflow["netflow"]),
                           dates_label=json.dumps(cashflow["labels"]),
                           cat_exp_amount=json.dumps(cat_exp_amount),
                           cat_exp_label=json.dumps(cat_exp_label),
                           cat_exp_amount_year=json.dumps(cat_exp_amount_year),
                           cat_exp_label_year=json.dumps(cat_exp_label_year),
                           cat_inc_amount=json.dumps(cat_inc_amount),
                           cat_inc_label=json.dumps(cat_inc_label),
                           cat_inc_amount_year=json.dumps(cat_inc_amount_year),
                           cat_inc_label_year=json.dumps(cat_inc_label_year),
                           selectionform=selectionform,
                           current_period=current_period)

@main_bp.route("/delete/<int:entry_id>", methods=["POST"])
def delete(entry_id):
    entry = TransactionHistory.query.get_or_404(entry_id)

    db.session.delete(entry)
    db.session.commit()

    flash("Successful Deletion", 'success')
    return redirect(url_for('main.show_transactions'))