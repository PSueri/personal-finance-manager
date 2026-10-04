from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError
from wtforms.fields import DateField

from application.categories import CATEGORY_TREE
from datetime import date, datetime

class UserInputForm(FlaskForm):
    TYPES = [(name, name) for name in CATEGORY_TREE]

    FIRST_CATEGORIES = list(dict.fromkeys(
        category
        for categories in CATEGORY_TREE.values()
        for category in categories
    ))

    SECOND_CATEGORIES = list(dict.fromkeys(
        subcategory
        for categories in CATEGORY_TREE.values()
        for subcategories in categories.values()
        for subcategory in subcategories
    ))

    type = SelectField(
        "Type",
        validators=[DataRequired(message="Select a transaction type.")],
        choices=[("", "Select...")] + TYPES,
    )

    first_category = SelectField(
        "First Category",
        validators=[DataRequired(message="Select a category.")],
        choices=[("", "Select...")] + [
            (name, name) for name in FIRST_CATEGORIES
        ],
    )

    second_category = SelectField(
        "Second Category",
        validators=[DataRequired(message="Select a subcategory.")],
        choices=[("", "Select...")] + [
            (name, name) for name in SECOND_CATEGORIES
        ],
    )

    date = DateField(
        "Date",
        validators=[InputRequired(message="Enter a date.")],
        format="%Y-%m-%d",
        default=date.today,
    )

    amount = IntegerField(
        "Amount",
        validators=[
            InputRequired(message="Enter an amount."),
            NumberRange(
                min=1,
                message="The amount must be greater than zero.",
            ),
        ],
    )

    submit = SubmitField("Add Transaction")

    def validate_first_category(self, field):
        categories = CATEGORY_TREE.get(self.type.data)

        if categories is None:
            return

        if field.data not in categories:
            raise ValidationError(
                "The category does not belong to the selected transaction type."
            )

    def validate_second_category(self, field):
        categories = CATEGORY_TREE.get(self.type.data, {})
        subcategories = categories.get(self.first_category.data)

        if subcategories is None:
            return

        if field.data not in subcategories:
            raise ValidationError(
                "The subcategory does not belong to the selected category."
            )

class SelectYearMonthForm(FlaskForm):
    year = datetime.today().year
    YEARS = [
        (year, str(year)), (year-1, str(year-1)), (year-2, str(year-2)), (year-3, str(year-3)), (year-4, str(year-4))
    ]
    MONTHS = [
        (1, 'Jan'), (2, 'Feb'), (3, 'Mar'), (4, 'Apr'), (5, 'May'), (6, 'Jun'),
        (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Oct'), (11, 'Nov'), (12, 'Dec')
    ]

    selected_year = SelectField('Select a Year', validators=[DataRequired()], choices=[(0, ' ')] + YEARS)
    selected_month = SelectField('Select a Month', validators=[DataRequired()], choices=[(0, ' ')] + MONTHS)
    submit = SubmitField("Refresh Data")