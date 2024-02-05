from application import app, db
from flask import render_template, flash, redirect, url_for, get_flashed_messages, request
from application.forms import UserInputForm, SelectYearMonthForm
from application.models import TransactionHistory
from flask_sqlalchemy import SQLAlchemy
import json
import pandas as pd
import calendar
from datetime import datetime

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
    selectionform = SelectYearMonthForm()
    if selectionform.validate_on_submit():
        # Assuming the year and month are passed as query parameters from the frontend
        year = selectionform.selected_year.data
        selmonth = selectionform.selected_month.data
    else:
        year=0
        selmonth=0
    # Set default values if not provided
    if not int(year):
        print('not year')
        year = datetime.now().year
    if not int(selmonth):
        print('not month')
        selmonth = datetime.now().month
    print(selmonth)
    current_period = str(year)+', '+calendar.month_name[int(selmonth)]
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

    month_amount = db.session.query(db.func.sum(TransactionHistory.amount),
                             db.func.extract('year',TransactionHistory.date),
                             db.func.extract('month',TransactionHistory.date)).group_by(
        db.func.extract('month',TransactionHistory.date),
        db.func.extract('year',TransactionHistory.date)).order_by(
        db.func.extract('month',TransactionHistory.date).desc(),
        db.func.extract('year',TransactionHistory.date).desc()).all()

    # Income DataFrame
    income=[]
    yearmonth=[]
    for amount, date in income_dates:
        income.append(amount)
        yearmonth.append(str(date.year)+" "+calendar.month_abbr[date.month])
    dict={'income':income, 'yearmonth':yearmonth}
    income_df=pd.DataFrame(data=dict)
    income_gouped=income_df.groupby("yearmonth", as_index=False).sum()

    # Expense DataFrame
    expense=[]
    yearmonth=[]
    for amount, date in expense_dates:
        expense.append(amount)
        yearmonth.append(str(date.year)+" "+calendar.month_abbr[date.month])
    dict={'expense':expense, 'yearmonth':yearmonth}
    expense_df=pd.DataFrame(data=dict)
    expense_gouped=expense_df.groupby("yearmonth", as_index=False).sum()

    # join df
    income_expense_dates_df=income_gouped.merge(expense_gouped, on='yearmonth', how='right').fillna(0)
    income_expense_dates_df["netflow"]=income_expense_dates_df["income"]-income_expense_dates_df["expense"]
    income_expense_dates_df["month"]=pd.to_datetime(income_expense_dates_df["yearmonth"].str[-3:], format='%b').dt.month
    income_expense_dates_df["year"]=pd.to_datetime(income_expense_dates_df["yearmonth"].str[:4], format='%Y').dt.year
    income_expense_dates_df=income_expense_dates_df.sort_values(by=['year', 'month'], ascending=True)
    print(income_expense_dates_df)
    # netflow
    netflow_month = income_expense_dates_df['netflow'].tolist()
    # label
    dates_label = income_expense_dates_df['yearmonth'].tolist()
    # incomes
    income_month = income_expense_dates_df['income'].tolist()
    # expenses
    expense_month = income_expense_dates_df['expense'].tolist()

    cat_exp_amount = []
    cat_exp_label = []
    for amount, category in category_expenses:
        cat_exp_label.append(category)
        cat_exp_amount.append(amount)

    cat_inc_amount = []
    cat_inc_label = []
    for amount, category in category_incomes:
        cat_inc_label.append(category)
        cat_inc_amount.append(amount)

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