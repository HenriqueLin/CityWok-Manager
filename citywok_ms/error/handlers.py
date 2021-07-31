from flask import Blueprint, render_template, redirect, abort
from flask.helpers import flash, url_for
from citywok_ms import db
from flask_babel import _
from flask_wtf.csrf import CSRFError

error_bp = Blueprint("error", __name__)


@error_bp.app_errorhandler(CSRFError)
def handle_csrf_error(error):
    flash(_("Session expired, please log in again."), "warning")
    return redirect(url_for("auth.login"))


@error_bp.app_errorhandler(401)
def unauthorized(error):
    flash(_("Please log in to access this page."), "info")
    return redirect(url_for("auth.login"))


@error_bp.app_errorhandler(403)
def forbidden(error):
    return render_template("error/403.html"), 403


@error_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("error/404.html"), 404


@error_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("error/500.html"), 500


@error_bp.route("/400")
def _400():
    abort(400)


@error_bp.route("/401")
def _401():
    abort(401)


@error_bp.route("/403")
def _403():
    abort(403)


@error_bp.route("/404")
def _404():
    abort(404)


@error_bp.route("/500")
def _500():
    abort(500)
