from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError
from wtforms.fields import DateField

from application.categories import CATEGORY_TREE
from application.money import parse_amount_to_cents
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

    amount = StringField(
        "Amount (€)",
        validators=[InputRequired(message="Enter an amount.")],
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

    def validate_amount(self, field):
        try:
            parse_amount_to_cents(field.data)
        except ValueError as error:
            raise ValidationError(str(error)) from error

class SelectYearMonthForm(FlaskForm):
    MONTHS = [
        (1, "Jan"), (2, "Feb"), (3, "Mar"), (4, "Apr"),
        (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Aug"),
        (9, "Sep"), (10, "Oct"), (11, "Nov"), (12, "Dec"),
    ]

    selected_year = SelectField(
        "Select a Year",
        coerce=int,
        validators=[
            InputRequired(message="Select a year."),
            NumberRange(min=1, message="Select a valid year."),
        ],
        default=lambda: datetime.today().year,
    )

    selected_month = SelectField(
        "Select a Month",
        coerce=int,
        choices=[(0, "Select...")] + MONTHS,
        validators=[
            InputRequired(message="Select a month."),
            NumberRange(
                min=1,
                max=12,
                message="Select a valid month.",
            ),
        ],
        default=lambda: datetime.today().month,
    )

    submit = SubmitField("Refresh Data")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_year = datetime.today().year

        self.selected_year.choices = [(0, "Select...")] + [(year, str(year)) for year in range(current_year, current_year - 5, -1)]