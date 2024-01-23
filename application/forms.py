from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired

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

    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField("Add Transaction")