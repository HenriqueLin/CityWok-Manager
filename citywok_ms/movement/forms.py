import datetime

from citywok_ms.employee.models import Employee
from citywok_ms.movement.models import (
    LABOR,
    LaborExpense,
    MATERIAL,
    OPERATION,
    TAX,
    NonLaborExpense,
)
from citywok_ms.supplier.models import Supplier
from citywok_ms.utils import FILEALLOWED
from citywok_ms.utils.fields import (
    BlankSelectField,
    FilesAllowed,
    FilesRequired,
    MultipleFileField,
)
from flask_babel import _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.core import FormField
from wtforms.fields.html5 import DateField, DecimalField
from wtforms.validators import (
    DataRequired,
    InputRequired,
    NumberRange,
    Optional,
    ValidationError,
)
from wtforms_alchemy.utils import choice_type_coerce_factory


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
    date = DateField(
        label=_l("Date"),
        validators=[InputRequired()],
        default=datetime.date.today(),
    )
    category = BlankSelectField(
        label=_l("Category"),
        choices=(
            (_l("Operation"), tuple((x, y) for x, y, _ in OPERATION)),
            (_l("Material"), tuple((x, y) for x, y, _ in MATERIAL)),
            (_l("Tax"), tuple((x, y) for x, y, _ in TAX)),
        ),
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
