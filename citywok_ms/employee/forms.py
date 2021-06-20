from datetime import date

from citywok_ms.employee.models import Employee
from citywok_ms.utils import ID, SEX
from citywok_ms.utils.fields import BlankCountryField, BlankSelectField
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import (
    DateField,
    DecimalField,
    EmailField,
    IntegerField,
    TelField,
)
from wtforms.validators import (
    Email,
    InputRequired,
    NumberRange,
    Optional,
    ValidationError,
)
from wtforms_alchemy.utils import choice_type_coerce_factory
from flask_babel import lazy_gettext as _l, _


class EmployeeForm(FlaskForm):
    hide_id = HiddenField()
    first_name = StringField(
        label=_l("First Name"),
        validators=[InputRequired()],
    )
    last_name = StringField(
        label=_l("Last Name"),
        validators=[InputRequired()],
    )
    zh_name = StringField(
        label=_l("Chinese Name"),
        filters=[lambda x: x or None],
        validators=[Optional()],
    )
    sex = BlankSelectField(
        label=_l("Sex"),
        choices=SEX,
        coerce=choice_type_coerce_factory(Employee.sex.type),
        message="---",
        validators=[InputRequired()],
    )
    birthday = DateField(
        label=_l("Birthday"),
        validators=[Optional()],
    )
    contact = TelField(
        label=_l("Contact"), validators=[Optional()], filters=[lambda x: x or None]
    )
    email = EmailField(
        label=_l("E-mail"),
        validators=[Optional(), Email()],
        filters=[lambda x: x or None],
    )
    id_type = BlankSelectField(
        label=_l("ID Type"),
        validators=[InputRequired()],
        choices=ID,
        coerce=choice_type_coerce_factory(Employee.id_type.type),
        message="---",
    )
    id_number = StringField(
        label=_l("ID Number"),
        validators=[InputRequired()],
    )
    id_validity = DateField(
        label=_l("ID Validity"),
        validators=[InputRequired()],
    )
    nationality = BlankCountryField(
        label=_l("Nationality"),
        message="---",
        validators=[InputRequired()],
    )
    nif = IntegerField(
        label=_l("NIF"),
        validators=[Optional()],
    )
    niss = IntegerField(
        label=_l("NISS"),
        validators=[Optional()],
    )
    employment_date = DateField(
        label=_l("Employment Date"),
        validators=[Optional()],
    )
    total_salary = DecimalField(
        label=_l("Total Salary"),
        validators=[InputRequired(), NumberRange(min=0)],
    )
    taxed_salary = DecimalField(
        label=_l("Taxed Salary"),
        validators=[InputRequired(), NumberRange(min=0)],
        default=635,
    )

    remark = TextAreaField(
        label=_l("Remark"),
        validators=[Optional()],
        filters=[lambda x: x or None],
    )

    submit = SubmitField(label=_l("Add"))
    update = SubmitField(label=_l("Update"))

    def validate_id_validity(self, id_validity):
        if self.id_validity.data and self.id_validity.data < date.today():
            raise ValidationError(_("ID has expired"))

    def validate_nif(self, nif):
        e = Employee.query.filter_by(nif=nif.data).first()
        if nif.data and e and (e.id != self.hide_id.data):
            raise ValidationError(_("This NIF already existe"))

    def validate_niss(self, niss):
        e = Employee.query.filter_by(niss=niss.data).first()
        if niss.data and e and (e.id != self.hide_id.data):
            raise ValidationError(_("This NISS already existe"))
