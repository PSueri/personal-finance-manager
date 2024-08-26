from application import app, db
from flask import render_template, flash, redirect, url_for, get_flashed_messages, request
from application.forms import UserInputForm, SelectYearMonthForm
from application.models import TransactionHistory
from flask_sqlalchemy import SQLAlchemy
import json
import requests
import pandas as pd
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

@app.route("/")
def index():
    return render_template('index.html', title='Home')

@app.route("/add", methods=["GET", "POST"])
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
        return redirect(url_for('show_transactions'))
    return render_template('add.html', title='Add', form=form)

@app.route("/transactions")
def show_transactions():
    entries=TransactionHistory.query.order_by(TransactionHistory.date.desc()).all()
    return render_template('show_transactions.html', title='Transactions', entries=entries)

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    def get_date_range_df(format_string="%Y %b"):
        """
        This function generates an ordered list of dates in the specified format
        from one year ago to the current month.

        Args:
            format_string (str, optional): The format string for the dates. Defaults to "%Y %b".

        Returns:
            list: A list of strings representing dates in the specified format.
        """
        today = datetime.today()
        one_year_ago = today - timedelta(days=365) + relativedelta(months=1)

        # Ensure the start date is at the beginning of the month
        one_year_ago = one_year_ago.replace(day=1)

        dates = []
        while one_year_ago <= today:
            dates.append(one_year_ago.strftime(format_string))
            one_year_ago = one_year_ago + relativedelta(months=1)
            dates_df = pd.DataFrame(dates, columns=['yearmonth'])
        return dates_df
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
    print(current_period)

    one_year_dates = get_date_range_df()
    print(one_year_dates)

    income_dates = db.session.query(db.func.sum(TransactionHistory.amount),
                                          TransactionHistory.date).filter_by(type='Income').group_by(
                                            TransactionHistory.date).order_by(
                                                TransactionHistory.date.desc()).all()
    expense_dates = db.session.query(db.func.sum(TransactionHistory.amount),
                                          TransactionHistory.date).filter_by(type='Expense').group_by(
                                            TransactionHistory.date).order_by(
                                                TransactionHistory.date.desc()).all()
    category_expenses = db.session.query(db.func.sum(TransactionHistory.amount),
                                           TransactionHistory.first_category).filter_by(type='Expense').filter(
                                            db.func.extract('year',TransactionHistory.date) == year).filter(
                                            db.func.extract('month',TransactionHistory.date) == selmonth).group_by(
                                             TransactionHistory.first_category).order_by(
                                             TransactionHistory.first_category).all()
    category_incomes = db.session.query(db.func.sum(TransactionHistory.amount),
                                           TransactionHistory.second_category).filter_by(type='Income').filter(
                                            db.func.extract('year',TransactionHistory.date) == year).filter(
                                            db.func.extract('month',TransactionHistory.date) == selmonth).group_by(
                                            TransactionHistory.second_category).order_by(
                                            TransactionHistory.second_category).all()

    income_dict = {
        "income": [amount for amount, _ in income_dates],
        "yearmonth": [f"{date.year} {calendar.month_abbr[date.month]}" for _, date in income_dates]
    }

    expense_dict = {
        "expense": [amount for amount, _ in expense_dates],
        "yearmonth": [f"{date.year} {calendar.month_abbr[date.month]}" for _, date in expense_dates]
    }

    # Create DataFrames for income and expenses
    income_df = pd.DataFrame(income_dict)
    expense_df = pd.DataFrame(expense_dict)

    # Group and sum using DataFrame methods
    income_grouped = income_df.groupby("yearmonth", as_index=False).sum()
    expense_grouped = expense_df.groupby("yearmonth", as_index=False).sum()

    # join df
    income_expense_dates_df = (one_year_dates.merge(income_grouped, on='yearmonth', how='left').fillna(0)
                               .merge(expense_grouped, on='yearmonth', how='left').fillna(0))
    income_expense_dates_df["netflow"] = income_expense_dates_df["income"] - income_expense_dates_df["expense"]
    income_expense_dates_df["month"] = pd.to_datetime(income_expense_dates_df["yearmonth"], format='%Y %b').dt.month
    income_expense_dates_df["year"] = pd.to_datetime(income_expense_dates_df["yearmonth"], format='%Y %b').dt.year
    income_expense_dates_df=income_expense_dates_df.sort_values(by=['year', 'month'], ascending=True)

    # netflow
    netflow_month = income_expense_dates_df['netflow'].tolist()
    # label
    dates_label = income_expense_dates_df['yearmonth'].tolist()
    # incomes
    income_month = income_expense_dates_df['income'].tolist()
    # expenses
    expense_month = income_expense_dates_df['expense'].tolist()

    # Create lists using list comprehension for monthly category amounts
    cat_exp_label = [category for _, category in category_expenses]
    cat_exp_amount = [amount for amount, _ in category_expenses]

    cat_inc_label = [category for _, category in category_incomes]
    cat_inc_amount = [amount for amount, _ in category_incomes]

    return render_template('dashboard.html', title='Dashboard',
                           income_month=json.dumps(income_month),
                           expense_month=json.dumps(expense_month),
                           netflow_month=json.dumps(netflow_month),
                           dates_label=json.dumps(dates_label),
                           cat_exp_amount=json.dumps(cat_exp_amount),
                           cat_exp_label=json.dumps(cat_exp_label),
                           cat_inc_amount=json.dumps(cat_inc_amount),
                           cat_inc_label=json.dumps(cat_inc_label),
                           selectionform=selectionform,
                           current_period=current_period)
@app.route("/delete/<int:entry_id>")
def delete(entry_id):
    entry = TransactionHistory.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Successful Deletion", 'success')
    return redirect(url_for('show_transactions'))