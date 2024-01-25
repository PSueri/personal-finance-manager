from application import app, db
from flask import render_template, flash, redirect, url_for, get_flashed_messages
from application.forms import UserInputForm
from application.models import TransactionHistory
from flask_sqlalchemy import SQLAlchemy
import json
import calendar

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

@app.route('/dashboard')
def dashboard():
    income_vs_expenses = db.session.query(db.func.sum(TransactionHistory.amount),
                    TransactionHistory.type).group_by(TransactionHistory.type).order_by(TransactionHistory.type).all()

    dates = db.session.query(db.func.sum(TransactionHistory.amount),
                             db.func.extract('year',TransactionHistory.date),
                             db.func.extract('month',TransactionHistory.date)).group_by(
        db.func.extract('month',TransactionHistory.date),
        db.func.extract('year',TransactionHistory.date)).order_by(
        db.func.extract('month',TransactionHistory.date),
        db.func.extract('year',TransactionHistory.date)).all()

    income_expense=[]
    for total_amount, _ in income_vs_expenses:
        income_expense.append(total_amount)

    over_time_expenditure = []
    dates_label = []
    for amount, year, month in dates:
        tmp_label=str(year)+" "+calendar.month_abbr[month]
        dates_label.append(tmp_label)
        over_time_expenditure.append(amount)
    return render_template('dashboard.html', title='Dashboard', income_vs_expenses=json.dumps(income_expense),
                           over_time_expenditure=json.dumps(over_time_expenditure), dates_label=json.dumps(dates_label))
@app.route("/delete/<int:entry_id>")
def delete(entry_id):
    entry = TransactionHistory.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Successful Deletion", 'success')
    return redirect(url_for('show_transactions'))