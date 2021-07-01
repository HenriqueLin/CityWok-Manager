from citywok_ms.utils import FILEALLOWED
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_babel import lazy_gettext as _l
from citywok_ms.utils.fields import MultipleFileField, FilesAllowed, FilesRequired
from wtforms.validators import InputRequired, NumberRange
from wtforms.fields.html5 import DateField, DecimalField


class OrderForm(FlaskForm):
    order_number = StringField(
        label=_l("Order Number"),
        validators=[InputRequired()],
    )
    delivery_date = DateField(
        label=_l("Delivery Date"),
        validators=[InputRequired()],
        default=datetime.date.today(),
    )
    value = DecimalField(
        label=_l("Value"),
        validators=[InputRequired(), NumberRange(min=0)],
    )

    files = MultipleFileField(
        label=_l("Files"),
        validators=[FilesRequired(), FilesAllowed(FILEALLOWED)],
    )

    submit = SubmitField(label=_l("Add"))
