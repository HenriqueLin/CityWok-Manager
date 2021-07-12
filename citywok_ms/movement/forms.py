from wtforms.fields.core import FormField
from citywok_ms.movement.models import Expense, CATEGORY
import datetime

from citywok_ms.supplier.models import Supplier
from citywok_ms.utils import FILEALLOWED
from citywok_ms.utils.fields import (
    BlankSelectField,
    FilesAllowed,
    FilesRequired,
    MultipleFileField,
)
from flask_babel import lazy_gettext as _l, _
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateField, DecimalField
from wtforms.validators import (
    DataRequired,
    InputRequired,
    NumberRange,
    Optional,
    ValidationError,
)
from wtforms_alchemy.utils import choice_type_coerce_factory
from citywok_ms.movement.models import NonLaborExpense


class MoneyForm(FlaskForm):
    cash = DecimalField(
        label=_l("Cash"),
        validators=[NumberRange(min=0)],
        default=0,
    )
    transfer = DecimalField(
        label=_l("Transfer"),
        validators=[NumberRange(min=0)],
        default=0,
    )
    card = DecimalField(
        label=_l("Card"),
        validators=[NumberRange(min=0)],
        default=0,
    )
    check = DecimalField(
        label=_l("Check"),
        validators=[NumberRange(min=0)],
        default=0,
    )

    def validate_cash(self, cash):
        if self.cash.data + self.card.data + self.transfer.data + self.check.data <= 0:
            raise ValidationError(_("Total value must be greater than 0."))


class NonLaborExpenseForm(FlaskForm):
    description = StringField(
        label=_l("Description"),
        validators=[InputRequired()],
    )
    date = DateField(
        label=_l("Date"),
        validators=[InputRequired()],
        default=datetime.date.today(),
    )
    category = BlankSelectField(
        label=_l("Category"),
        choices=CATEGORY[1:],
        coerce=choice_type_coerce_factory(NonLaborExpense.category.type),
        message="---",
        validators=[InputRequired()],
    )
    value = FormField(MoneyForm)

    supplier = QuerySelectField(
        label=_l("Supplier"),
        query_factory=lambda: Supplier.query,
        get_pk=lambda x: x.id,
        get_label=lambda x: f"{x.id}: {x.name}",
        allow_blank=True,
        blank_text="---",
        validators=[DataRequired()],
    )
    remark = TextAreaField(
        label=_l("Remark"),
        validators=[Optional()],
        filters=[lambda x: x or None],
    )

    files = MultipleFileField(
        label=_l("Files"),
        validators=[FilesRequired(), FilesAllowed(FILEALLOWED)],
    )

    submit = SubmitField(label=_l("Add"))
