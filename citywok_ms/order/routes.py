from sqlalchemy.sql.elements import not_
from citywok_ms import db
from citywok_ms.auth.permissions import manager, shareholder
from citywok_ms.file.forms import FileForm
from citywok_ms.file.models import File, OrderFile
from citywok_ms.order.forms import OrderForm, OrderUpdateForm
from citywok_ms.order.models import Order
from citywok_ms.task import compress_file
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_babel import _
from flask_login.utils import login_required
from sqlalchemy import func

order_bp = Blueprint("order", __name__, url_prefix="/order")


@order_bp.route("/")
@login_required
@shareholder.require(403)
def index():
    payed_page = request.args.get("payed_page", 1, type=int)
    unpayed_page = request.args.get("unpayed_page", 1, type=int)
    unpayed_query = db.session.query(Order).filter(Order.expense_id.is_(None))
    unpay_value = (
        unpayed_query.with_entities(func.coalesce(func.sum(Order.value), 0))
        .filter(not_(Order.expense.has()))
        .first()[0]
    )
    return render_template(
        "order/index.html",
        title=_("Order"),
        payed=db.session.query(Order)
        .filter(Order.expense_id.isnot(None))
        .order_by(Order.delivery_date.desc())
        .paginate(page=payed_page, per_page=10),
        unpayed=unpayed_query.order_by(Order.delivery_date.desc()).paginate(
            page=unpayed_page, per_page=10
        ),
        unpay_value=unpay_value,
    )


@order_bp.route("/new", methods=["GET", "POST"])
@login_required
@manager.require(403)
def new():
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(
            order_number=form.order_number.data,
            delivery_date=form.delivery_date.data,
            value=form.value.data,
            supplier=form.supplier.data,
        )
        for f in form.files.data or []:
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
        return redirect(url_for("order.index"))
    return render_template("order/new.html", title=_("New Order"), form=form)


@order_bp.route("/<order_id>/update", methods=["GET", "POST"])
@login_required
@manager.require(403)
def update(order_id):
    order = Order.get_or_404(order_id)
    form = OrderUpdateForm()
    form.hide_id.data = order.id

    if form.validate_on_submit():
        order.update_by_form(form)
        flash(
            _("Order has been updated."),
            "success",
        )
        db.session.commit()
        current_app.logger.info(f"Update order {order}")
        return redirect(url_for("order.detail", order_id=order_id))

    form.process(obj=order)

    return render_template(
        "order/update.html",
        order=order,
        form=form,
        title=_("Update Order"),
    )


@order_bp.route("/<int:order_id>")
@login_required
@shareholder.require(403)
def detail(order_id):
    order = Order.get_or_404(order_id)
    return render_template(
        "order/detail.html",
        title=_("Order Detail"),
        order=order,
        file_form=FileForm(),
    )


@order_bp.route("/<int:order_id>/upload", methods=["POST"])
@login_required
@manager.require(403)
def upload(order_id):
    form = FileForm()
    file = form.file.data
    if form.validate_on_submit():
        db_file = OrderFile.create(form.file.data)
        db_file.order_id = order_id
        flash(
            _('File "%(name)s" has been uploaded.', name=db_file.full_name), "success"
        )
        db.session.commit()
        current_app.logger.info(f"Upload employee file {db_file}")
        compress_file.queue(db_file.id)

    elif file is not None:
        flash(
            _('Invalid file format "%(format)s".', format=File.split_file_format(file)),
            "danger",
        )
    else:
        flash(_("No file has been uploaded."), "danger")
    return redirect(url_for("order.detail", order_id=order_id))
