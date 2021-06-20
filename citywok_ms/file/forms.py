from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, Optional
from citywok_ms.utils import FILEALLOWED
from flask_babel import lazy_gettext as _l


class FileForm(FlaskForm):
    file = FileField(
        label=_l("File"),
        validators=[
            FileRequired(),
            FileAllowed(FILEALLOWED),
        ],
    )


class FileUpdateForm(FlaskForm):
    file_name = StringField(label=_l("File Name"), validators=[InputRequired()])
    remark = TextAreaField(label=_l("Remark"), validators=[Optional()])
    update = SubmitField(label=_l("Update"))
