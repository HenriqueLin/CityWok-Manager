import citywok_ms.auth.messages as auth_msg
from citywok_ms.auth.forms import LoginForm
from citywok_ms.auth.models import User
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from flask_principal import AnonymousIdentity, Identity, identity_changed

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
            login_user(user)
            identity_changed.send(
                current_app._get_current_object(), identity=Identity(user.id)
            )
            flash(auth_msg.LOGIN_SUCCESS.format(name=user.username), category="success")
            # FIXME: main index page
            return redirect(url_for("employee.index"))
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
