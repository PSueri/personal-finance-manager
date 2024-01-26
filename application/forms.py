from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import DateField
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import DateField
from datetime import datetime

class UserInputForm(FlaskForm):
    TYPES = [('Income', 'Income'), ('Expense', 'Expense')]

    FIRST_CATEGORIES = [
        ('Work', 'Work'), ('OtherIncome', 'OtherIncome'), ('Home', 'Home'),
        ('Cash', 'Cash'), ('Bills', 'Bills'), ('Food', 'Food'),
        ('Taxes', 'Taxes'), ('Transportation', 'Transportation'),
        ('LoanOrSubscription', 'LoanOrSubscription'), ('OtherExpense', 'OtherExpense')
    ]

    SECOND_CATEGORIES = [
        ('Salary', 'Salary'), ('Bonus', 'Bonus'), ('ThirteenthSalary', 'ThirteenthSalary'),
        ('Gift', 'Gift'), ('OtherIncome', 'OtherIncome'), ('Rent', 'Rent'),
        ('Grocery', 'Grocery'), ('Cash', 'Cash'), ('Light', 'Light'), ('Fine', 'Fine'),
        ('OtherBill', 'OtherBill'), ('Restourant', 'Restourant'), ('TakeAway', 'TakeAway'),
        ('Bar', 'Bar'), ('Bank', 'Bank'), ('OtherTaxes', 'OtherTaxes'),
        ('CarRent', 'CarRent'), ('PublicTransport', 'PublicTransport'), ('Loan', 'Loan'),
        ('PSPlus', 'PSPlus'), ('CrunchyRoll', 'CrunchyRoll'), ('FantasyFootball', 'FantasyFootball'),
        ('Telephone', 'Telephone'), ('Cigarettes', 'Cigarettes'), ('Present', 'Present'), ('Other', 'Other')
    ]

    type = SelectField('Type', validators=[DataRequired()], choices=[('Select', ' ')] + TYPES)

    first_category = SelectField('First Category', validators=[DataRequired()], choices=[('Select', ' ')] + FIRST_CATEGORIES)

    second_category = SelectField('Second Category', validators=[DataRequired()], choices=[('Select', ' ')] + SECOND_CATEGORIES)

    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.now())

    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField("Add Transaction")