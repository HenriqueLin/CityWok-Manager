from citywok_ms.task import compress_file
from citywok_ms.movement.order.models import Order
from citywok_ms.movement.order.forms import OrderForm
from flask import Blueprint, flash, redirect, url_for, render_template, current_app
from citywok_ms.auth.permissions import manager
from citywok_ms import db
from flask_babel import _
from citywok_ms.file.models import OrderFile

order_bp = Blueprint("order", __name__, url_prefix="/order")


@order_bp.route("/new", methods=["GET", "POST"])
@manager.require(403)
def new():
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(
            order_number=form.order_number.data,
            delivery_date=form.delivery_date.data,
            value=form.value.data,
        )
        for f in form.files.data:
            db_file = OrderFile.create(f)
            order.files.append(db_file)
            compress_file.queue(db_file.id)
        db.session.add(order)
        flash(
            _("New order has been registe."),
            "success",
        )
        db.session.commit()
        current_app.logger.info(f"Create order {order}")
        return redirect(url_for("order.new"))  # FIXME:
    return render_template("movement/order/new.html", title=_("New Order"), form=form)
