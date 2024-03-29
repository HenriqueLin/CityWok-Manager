from citywok_ms.income.models import Revenue
import datetime
from citywok_ms.utils import FILEALLOWED
from citywok_ms.utils.fields import FilesAllowed, FilesRequired, MultipleFileField
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.fields.core import FieldList, FormField
from wtforms.fields.html5 import DateField, DecimalField
from wtforms.validators import (
    DataRequired,
    InputRequired,
    NumberRange,
    Optional,
    ValidationError,
)
from citywok_ms import db
from citywok_ms.expense.forms import MoneyForm


class CardForm(FlaskForm):
    total = DecimalField(
        label=_l("Total"),
        default=0,
        validators=[NumberRange(min=0), InputRequired()],
    )
    actual = DecimalField(
        label=_l("Actual"),
        default=0,
        validators=[NumberRange(min=0), InputRequired()],
    )

    @property
    def fee(self):
        return self.total.data - self.actual.data

    def validate_total(self, total):
        if self.total.data < self.actual.data:
            raise ValidationError(_l("Total value must be greater than actual."))


class RevenueForm(FlaskForm):
    date = DateField(
        label=_l("Date"),
        validators=[InputRequired()],
        default=datetime.date.today,
    )
    t_revenue = DecimalField(
        label=_l("Theoretical Revenue"),
        validators=[NumberRange(min=0)],
        default=0,
    )
    cash = DecimalField(
        label=_l("Cash"),
        validators=[NumberRange(min=0)],
        default=0,
    )
    cards = FieldList(
        FormField(CardForm),
        label="Cards",
        max_entries=3,
        min_entries=3,
    )
    remark = TextAreaField(
        label=_l("Remark"),
        validators=[Optional()],
        filters=[lambda x: x or None],
    )
    files = MultipleFileField(
        label=_l("Files"),
        validators=[FilesAllowed(FILEALLOWED)],
    )
    submit = SubmitField(label=_l("Add"))

    @property
    def cards_fee(self):
        return sum([card.fee for card in self.cards])

    def validate_date(self, date):
        if db.session.query(Revenue).get(self.date.data):
            raise ValidationError(
                _l('Revenue of "%(date)s" already existe.', date=self.date.data)
            )


class IncomeForm(FlaskForm):
    date = DateField(
        label=_l("Date"),
        validators=[InputRequired()],
        default=datetime.date.today,
    )
    value = FormField(MoneyForm)
    remark = TextAreaField(
        label=_l("Remark"),
        validators=[Optional()],
        filters=[lambda x: x or None],
    )
    files = MultipleFileField(
        label=_l("Files"),
        validators=[FilesAllowed(FILEALLOWED)],
    )

    submit = SubmitField(label=_l("Add"))
    update = SubmitField(label=_l("Update"))
