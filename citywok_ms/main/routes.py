from flask import Blueprint, render_template
from citywok_ms.auth.permissions import visitor

main_bp = Blueprint("main", __name__)


@main_bp.route("/home")
@visitor.require(401)
def index():
    return render_template("main/index.html", title="Home")
