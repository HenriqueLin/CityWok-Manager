import datetime

from citywok_ms import db
from citywok_ms.order.models import Order
from citywok_ms.supplier.models import Supplier
from citywok_ms.utils import FILEALLOWED
from citywok_ms.utils.fields import FilesAllowed, MultipleFileField
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateField, DecimalField
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Optional,
    ValidationError,
)


class OrderForm(FlaskForm):
    order_number = StringField(
        label=_l("Order Number"),
        validators=[InputRequired()],
    )
    delivery_date = DateField(
        label=_l("Delivery Date"),
        validators=[InputRequired()],
        default=datetime.date.today,
    )
    value = DecimalField(
        label=_l("Value"),
        validators=[InputRequired()],
    )

    supplier = QuerySelectField(
        label=_l("Supplier"),
        query_factory=lambda: Supplier.query,
        get_pk=lambda x: x.id,
        get_label=lambda x: f"{x.id}: {x.name}",
        allow_blank=True,
        blank_text="---",
        validators=[DataRequired()],
    )

    files = MultipleFileField(
        label=_l("Files"),
        validators=[FilesAllowed(FILEALLOWED)],
    )
    remark = TextAreaField(
        label=_l("Remark"),
        validators=[Optional()],
        filters=[lambda x: x or None],
    )

    submit = SubmitField(label=_l("Add"))

    def validate_order_number(self, order_number):
        exist = (
            db.session.query(Order)
            .filter(
                Order.order_number == self.order_number.data,
                Order.supplier_id == self.supplier.data.id,
            )
            .first()
        )
        if exist:
            raise ValidationError(_l("Order Number already exists."))


class OrderUpdateForm(FlaskForm):
    hide_id = HiddenField()

    order_number = StringField(
        label=_l("Order Number"),
        validators=[InputRequired()],
    )
    delivery_date = DateField(
        label=_l("Delivery Date"),
        validators=[InputRequired()],
        default=datetime.date.today,
    )
    value = DecimalField(
        label=_l("Value"),
        validators=[InputRequired()],
    )

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

    submit = SubmitField(label=_l("Update"))
