from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import DateField
from datetime import datetime

class UserInputForm(FlaskForm):
    type = SelectField('Type', validators=[DataRequired()],
                                    choices =[('Income', 'Income'),
                                               ('Expense', 'Expense')])

    first_category = SelectField('First Category', validators=[DataRequired()],
                                    choices =[('Work', 'Work'),
                                               ('Home', 'Home')])

    second_category = SelectField('Second Category', validators=[DataRequired()],
                                    choices =[('Salary', 'Salary'),
                                               ('Rent', 'Rent')])
    date = DateField('Date', validators=[DataRequired()],
                                    format='%Y-%m-%d', default=datetime.now())

    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField("Add Transaction")