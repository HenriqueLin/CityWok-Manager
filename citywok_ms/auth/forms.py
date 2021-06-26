from citywok_ms.auth.models import Role, User
from citywok_ms.utils.fields import BlankSelectField
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Length, ValidationError
from wtforms_alchemy.utils import choice_type_coerce_factory
from flask_babel import lazy_gettext as _l, _


class LoginForm(FlaskForm):
    username = StringField(
        label=_l("User Name"),
        validators=[InputRequired(), Length(min=2, max=20)],
    )
    password = PasswordField(
        label=_l("Password"),
        validators=[InputRequired()],
    )

    submit = SubmitField(label=_l("Login"))


class InviteForm(FlaskForm):
    email = EmailField(
        label=_l("Invitee's E-mail"),
        validators=[InputRequired(), Email()],
    )
    role = BlankSelectField(
        label=_l("Role"),
        choices=Role[1:],
        coerce=choice_type_coerce_factory(User.role.type),
        message="---",
        validators=[InputRequired()],
    )
    submit = SubmitField(label=_l("Invite"))

    def validate_email(self, email):
        if User.get_by_email(email.data):
            raise ValidationError(_("E-mail address already taken."))


class ForgetPasswordForm(FlaskForm):
    email = EmailField(
        label=_l("Email"),
        validators=[InputRequired(), Email()],
    )
    submit = SubmitField(_l("Submit"))

    def validate_email(self, email):
        if not User.get_by_email(email.data):
            raise ValidationError(_("User with this e-mail address do not exist."))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        label=_l("New Password"),
        validators=[InputRequired()],
    )
    password2 = PasswordField(
        label=_l("Repeat Password"),
        validators=[InputRequired(), EqualTo("password")],
    )
    submit = SubmitField(label=_l("Reset"))


class RegistrationForm(FlaskForm):
    username = StringField(
        label=_l("User Name"),
        validators=[InputRequired()],
    )
    password = PasswordField(
        label=_l("Password"),
        validators=[InputRequired()],
    )
    password2 = PasswordField(
        label=_l("Repeat Password"),
        validators=[InputRequired(), EqualTo("password")],
    )
    submit = SubmitField(label=_l("Register"))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_("Please use a different username."))
