from flask import Blueprint, render_template, redirect, abort
from flask.helpers import flash, url_for
from citywok_ms import db
from flask_babel import _

error = Blueprint("error", __name__)


@error.app_errorhandler(401)
def unauthorized(error):
    flash(_("Please log in to access this page."), "info")
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


@error.route("/401")
def _401():
    abort(401)


@error.route("/403")
def _403():
    abort(403)


@error.route("/404")
def _404():
    abort(404)


@error.route("/500")
def _500():
    abort(500)
