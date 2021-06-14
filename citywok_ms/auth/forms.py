from citywok_ms.auth.models import Role, User
from citywok_ms.utils.fields import BlankSelectField
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Length, ValidationError
from wtforms_alchemy.utils import choice_type_coerce_factory


class LoginForm(FlaskForm):
    username = StringField(
        "User Name",
        validators=[InputRequired(), Length(min=2, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired()],
    )

    submit = SubmitField(label="Login")


class InviteForm(FlaskForm):
    email = EmailField(
        label="Invitee's E-mail",
        validators=[InputRequired(), Email()],
    )
    role = BlankSelectField(
        label="Role",
        choices=Role[1:],
        coerce=choice_type_coerce_factory(User.role.type),
        message="---",
        validators=[InputRequired()],
    )
    submit = SubmitField(label="Invite")


class RegistrationForm(FlaskForm):
    username = StringField(
        label="Username",
        validators=[InputRequired()],
    )
    email = StringField(
        label="Email",
        validators=[InputRequired(), Email()],
    )
    password = PasswordField(
        label="Password",
        validators=[InputRequired()],
    )
    password2 = PasswordField(
        label="Repeat Password",
        validators=[InputRequired(), EqualTo("password")],
    )
    submit = SubmitField(label="Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")
