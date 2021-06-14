from citywok_ms.email import send_confirmation_email, send_invite_email
import citywok_ms.auth.messages as auth_msg
from citywok_ms.auth.forms import InviteForm, LoginForm, RegistrationForm
from citywok_ms.auth.models import User
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
    request,
)
from flask_login import current_user, login_user, logout_user
from flask_principal import AnonymousIdentity, Identity, identity_changed
from citywok_ms.auth.permissions import manager

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        # FIXME: after create a main index page
        return redirect(url_for("employee.index"))
    if form.validate_on_submit():
        user = User.authenticate_user(
            username=form.username.data, password=form.password.data
        )
        if user:
            if user.confirmed:
                login_user(user)
                identity_changed.send(
                    current_app._get_current_object(), identity=Identity(user.id)
                )
                flash(
                    auth_msg.LOGIN_SUCCESS.format(name=user.username),
                    category="success",
                )
                # FIXME: main index page
                return redirect(url_for("employee.index"))
            else:
                flash(auth_msg.REQUIRE_CONFIRMATION, "warning")
                return redirect(url_for("auth.login"))
        else:
            flash(auth_msg.LOGIN_FAIL, category="danger")
    return render_template("auth/login.html", title=auth_msg.LOGIN_TITLE, form=form)


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    identity_changed.send(
        current_app._get_current_object(), identity=AnonymousIdentity()
    )
    flash(auth_msg.LOGOUT_SUCCESS, category="success")
    return redirect(url_for("auth.login"))


@auth.route("/invite", methods=["GET", "POST"])
@manager.require(403)
def invite():
    form = InviteForm()
    if request.method == "GET":
        token = request.args.get("token")
    if form.validate_on_submit():
        token = User.create_invite_token(form.role.data, form.email.data)
        send_invite_email(form.email.data, token)
        flash(auth_msg.EMAIL_SENT, "success")
        return redirect(url_for("auth.invite", token=token))

    return render_template(
        "auth/invite.html",
        title=auth_msg.INVITE_TITLE,
        form=form,
        token=token,
    )


@auth.route("/registration/<token>", methods=["GET", "POST"])
def registration(token):
    if current_user.is_authenticated:
        flash(auth_msg.REQUIRED_LOGOUT, "warning")
        # FIXME: to main page
        return redirect(url_for("employee.index"))
    role, email = User.verify_invite_token(token)
    if not role:
        flash(auth_msg.INVALID_INVITE, "warning")
        return redirect(url_for("auth.login"))
    form = RegistrationForm()
    if request.method == "GET":
        form.email.data = email
    elif request.method == "POST":
        if form.validate_on_submit():
            user = User.create_by_form(form, role)
            token = User.create_confirmation_token(user.id, user.email, user.username)
            send_confirmation_email(user.email, token, user.username)
            flash(
                auth_msg.REGISTE_SUCCESS.format(email=form.email.data),
                category="success",
            )
            return redirect(url_for("auth.login"))

    return render_template(
        "auth/registration.html",
        title=auth_msg.REGISTE_TITLE,
        form=form,
    )


@auth.route("/confirmation/<token>")
def confirmation(token):
    if current_user.is_authenticated:
        flash(auth_msg.REQUIRED_LOGOUT, "warning")
        # FIXME: to main page
        return redirect(url_for("employee.index"))

    user = User.verify_confirmation_token(token)
    if user:
        if user.confirmed:
            flash(auth_msg.ALREADY_CONFIRMED, "info")
        else:
            user.confirm()
            flash(auth_msg.CONFIRMATION_SUCCESS, "success")
    else:
        flash(auth_msg.INVALID_CONFIRMATION, "warning")

    return redirect(url_for("auth.login"))
