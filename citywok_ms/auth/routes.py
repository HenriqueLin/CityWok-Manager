from citywok_ms import db
from citywok_ms.auth.forms import (
    ForgetPasswordForm,
    InviteForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
)
from citywok_ms.auth.models import User
from citywok_ms.auth.permissions import manager
from citywok_ms.email import (
    send_invite_email,
    send_password_reset_email,
)
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_babel import _
from flask_login import current_user, login_user, logout_user
from flask_principal import AnonymousIdentity, Identity, identity_changed

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        user = User.authenticate_user(
            username=form.username.data, password=form.password.data
        )
        if user:
            login_user(user)
            identity_changed.send(
                current_app._get_current_object(), identity=Identity(user.id)
            )
            flash(
                _("Welcome %(name)s, you are logged in.", name=user.username),
                category="success",
            )
            current_app.logger.info("Log in")
            return redirect(url_for("main.index"))
        else:
            flash(_("Please check your username/password."), category="danger")
    return render_template("auth/login.html", title=_("Login"), form=form)


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    current_app.logger.info("Log out")
    logout_user()
    identity_changed.send(
        current_app._get_current_object(), identity=AnonymousIdentity()
    )
    flash(_("You have been logged out."), category="success")
    return redirect(url_for("auth.login"))


@auth.route("/invite", methods=["GET", "POST"])
@manager.require(403)
def invite():
    form = InviteForm()
    if form.validate_on_submit():
        token = User.create_invite_token(form.role.data, form.email.data)
        send_invite_email(form.email.data, token)
        flash(_("A invite e-mail has been sent to the envitee."), "success")
        current_app.logger.info(f"Invite {form.email.data} as {form.role.data}")
        return redirect(url_for("auth.invite"))

    return render_template(
        "auth/invite.html",
        title=_("Invite"),
        form=form,
    )


@auth.route("/registration/<token>", methods=["GET", "POST"])
def registration(token):
    if current_user.is_authenticated:
        flash(_("You are already logged in."), "warning")
        return redirect(url_for("main.index"))
    role, email = User.verify_invite_token(token) or (None, None)
    if not role:
        flash(_("Invite link is invalid."), "warning")
        return redirect(url_for("auth.login"))
    if User.get_by_email(email) is not None:
        flash(_("This email has already been registed."), "warning")
        return redirect(url_for("auth.login"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.create_by_form(form, role)
        user.email = email
        flash(
            _("You are now registed."),
            category="success",
        )
        db.session.commit()
        current_app.logger.info(f"{user} registe")
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/registration.html",
        title=_("Register"),
        form=form,
    )


@auth.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        token = user.create_reset_token()
        send_password_reset_email(user, token)
        flash(
            _(
                "A e-mail to reset the password has been sent to %(email)s.",
                email=form.email.data,
            ),
            "success",
        )
        current_app.logger.info(f"{user} forgot password")
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/forget_password.html", title=_("Forget Password"), form=form
    )


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user = User.verify_reset_token(token)
    if user:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            user.set_password(form.password.data)
            flash(_("Your password has been reset."), "success")
            db.session.commit()
            current_app.logger.info(f"{user} reset password")
            return redirect(url_for("auth.login"))
    else:
        flash(_("Reset link is invalid."), "warning")
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password.html", title=_("Reset Password"), form=form
    )
