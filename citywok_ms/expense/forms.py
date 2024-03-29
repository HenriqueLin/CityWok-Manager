import datetime

from citywok_ms.employee.models import Employee
from citywok_ms.expense.models import (
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
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields.core import BooleanField, FormField
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
    def __init__(self, formdata, **kwargs):
        super().__init__(formdata=formdata, **kwargs)
        self.form_errors = []

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

    @property
    def total(self):
        return sum(
            filter(
                None,
                [self.cash.data, self.card.data, self.transfer.data, self.check.data],
            )
        )

    @property
    def errors(self):
        errors = {name: f.errors for name, f in self._fields.items() if f.errors}
        if self.form_errors:
            errors[None] = self.form_errors
        return errors

    def validate(self, extra_validators=None):
        if self.total <= 0:
            self.form_errors.append(_l("Total value must be greater than 0."))
            return False
        return super().validate(extra_validators=extra_validators)


class NonLaborExpenseForm(FlaskForm):
    date = DateField(
        label=_l("Date"),
        validators=[InputRequired()],
        default=datetime.date.today,
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
        validators=[FilesAllowed(FILEALLOWED)],
    )
    from_pos = BooleanField(
        label=_l("From POS"),
        default=False,
    )

    submit = SubmitField(label=_l("Add"))
    update = SubmitField(label=_l("Update"))

    def validate_from_pos(self, from_pos):
        if (
            self.from_pos.data
            and sum(
                filter(
                    None,
                    [
                        self.value.card.data,
                        self.value.transfer.data,
                        self.value.check.data,
                    ],
                )
            )
            > 0
        ):
            raise ValidationError(_l("Expense from POS must be payed with cash."))


class OrderPaymentForm(FlaskForm):
    date = DateField(
        label=_l("Date"),
        validators=[InputRequired()],
        default=datetime.date.today,
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
    orders = QuerySelectMultipleField(
        label=_l("Orders"),
        get_pk=lambda x: x.id,
        get_label=lambda x: f"{x.order_number}: {x.value}",
        validators=[DataRequired()],
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

    load = SubmitField()
    submit = SubmitField(label=_l("Add"))
    update = SubmitField(label=_l("Update"))


class LaborExpenseForm(FlaskForm):
    category = BlankSelectField(
        label=_l("Category"),
        choices=tuple((x, y) for x, y, _ in LABOR if x != "labor:salary"),
        coerce=choice_type_coerce_factory(LaborExpense.category.type),
        message="---",
        validators=[InputRequired()],
    )
    date = DateField(
        label=_l("Date"),
        validators=[InputRequired()],
        default=datetime.date.today,
    )
    value = FormField(MoneyForm)

    employee = QuerySelectField(
        label=_l("Employee"),
        query_factory=lambda: Employee.query.filter(Employee.active),
        get_pk=lambda x: x.id,
        get_label=lambda x: f"{x.id}: {x.full_name}",
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
        validators=[FilesAllowed(FILEALLOWED)],
    )
    from_pos = BooleanField(
        label=_l("From POS"),
        default=False,
    )

    submit = SubmitField(label=_l("Add"))
    update = SubmitField(label=_l("Update"))

    def validate_from_pos(self, from_pos):
        if (
            self.from_pos.data
            and sum(
                filter(
                    None,
                    [
                        self.value.card.data,
                        self.value.transfer.data,
                        self.value.check.data,
                    ],
                )
            )
            > 0
        ):
            raise ValidationError(_l("Expense from POS must be payed with cash."))


class DateForm(FlaskForm):
    date = DateField(
        label=_l("Date"),
        default=datetime.datetime.today,
        validators=[InputRequired()],
    )


class MonthForm(FlaskForm):
    month = DateField(
        label=_l("Month"),
        default=datetime.datetime.today,
        validators=[InputRequired()],
        format="%Y-%m",
        render_kw={"type": "month"},
    )


class SalaryForm(FlaskForm):
    date = DateField(
        label=_l("Payment Date"),
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
