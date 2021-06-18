from citywok_ms.auth.messages import REQUIRE_LOGIN
from flask import Blueprint, render_template, redirect
from flask.helpers import flash, url_for

error = Blueprint("error", __name__)


@error.app_errorhandler(401)
def unauthorized(error):
    flash(REQUIRE_LOGIN, "info")
    return redirect(url_for("auth.login"))

