from citywok_ms.supplier.models import Supplier
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField, IntegerField, TelField
from wtforms.validators import Email, InputRequired, Optional, ValidationError
from flask_babel import lazy_gettext as _l, _


class SupplierForm(FlaskForm):
    hide_id = HiddenField()
    name = StringField(
        label=_l("Company Name"),
        validators=[InputRequired()],
    )
    abbreviation = StringField(
        label=_l("Abbreviation"),
        validators=[Optional()],
    )
    principal = StringField(
        label=_l("Principal"),
        validators=[InputRequired()],
    )
    contact = TelField(
        label=_l("Contact"),
        validators=[Optional()],
    )

    email = EmailField(
        label=_l("E-mail"),
        validators=[Optional(), Email()],
    )
    nif = IntegerField(
        label=_l("NIF"),
        validators=[Optional()],
    )
    iban = StringField(
        label=_l("IBAN"),
        validators=[Optional()],
        filters=[lambda x: x or None],
    )
    address = StringField(
        label=_l("Address"),
        validators=[Optional()],
    )
    postcode = StringField(
        label=_l("Postcode"),
        validators=[Optional()],
    )
    city = StringField(
        label=_l("City"),
        validators=[Optional()],
    )

    remark = TextAreaField(
        label=_l("Remark"),
        validators=[Optional()],
    )

    submit = SubmitField(label=_l("Add"))
    update = SubmitField(label=_l("Update"))

    def validate_nif(self, nif):
        s = Supplier.query.filter_by(nif=nif.data).first()
        if nif.data and s and (s.id != self.hide_id.data):
            raise ValidationError(_("This NIF already existe"))

    def validate_iban(self, iban):
        s = Supplier.query.filter_by(iban=iban.data).first()
        if iban.data and s and (s.id != self.hide_id.data):
            raise ValidationError(_("This IBAN already existe"))
