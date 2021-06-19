from citywok_ms.auth.messages import REQUIRE_LOGIN
from flask import Blueprint, render_template, redirect
from flask.helpers import flash, url_for
from citywok_ms import db

error = Blueprint("error", __name__)


@error.app_errorhandler(401)
def unauthorized(error):
    flash(REQUIRE_LOGIN, "info")
    return redirect(url_for("auth.login"))


@error.app_errorhandler(403)
def forbidden(error):
    return render_template("error/403.html"), 403


@error.app_errorhandler(404)
def not_found_error(error):
    return render_template("error/404.html"), 404


@error.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("error/500.html"), 500
