from application import app, db
from flask import render_template, flash, redirect, url_for, get_flashed_messages
from application.forms import UserInputForm
from application.models import TransactionHistory

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
                                 amount=form.amount.data)
        db.session.add(entry)
        db.session.commit()
        flash("Successful entry", 'success')
        return redirect(url_for('index'))
    return render_template('add.html', title='Add', form=form)