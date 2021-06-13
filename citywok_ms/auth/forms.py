from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "User Name",
        validators=[InputRequired(), Length(min=2, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired()],
    )

    submit = SubmitField(label="Submit")
