from flask_login.utils import login_required
from sqlalchemy import func
from sqlalchemy.sql.elements import not_
from citywok_ms import db
from citywok_ms.auth.permissions import manager, shareholder, visitor
from citywok_ms.expense.models import NonLaborExpense
from citywok_ms.file.forms import FileForm
from citywok_ms.file.models import File, SupplierFile
from citywok_ms.order.models import Order
from citywok_ms.supplier.forms import SupplierForm
from citywok_ms.supplier.models import Supplier
from citywok_ms.task import compress_file
from citywok_ms.expense.models import Expense
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask.globals import current_app
from flask_babel import _

supplier_bp = Blueprint("supplier", __name__, url_prefix="/supplier")


@supplier_bp.route("/")
@login_required
@visitor.require(401)
def index():
    keys = (
        ("id", _("ID")),
        ("name", _("Company Name")),
        ("principal", _("Principal")),
        ("abbreviation", _("Abbreviation")),
        ("nif", _("NIF")),
        ("iban", _("IBAN")),
        ("contact", _("Contact")),
        ("email", _("E-mail")),
    )
    sort = request.args.get("sort") or "id"
    desc = request.args.get("desc") or False
    return render_template(
        "supplier/index.html",
        title=_("Suppliers"),
        suppliers=Supplier.get_all(sort, desc),
        keys=keys,
        sort=sort,
        desc=desc,
    )


@supplier_bp.route("/new", methods=["GET", "POST"])
@login_required
@manager.require(403)
def new():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier.create_by_form(form)
        flash(
            _('New supplier "%(name)s" has been added.', name=supplier.name), "success"
        )
        db.session.commit()
        current_app.logger.info(f"Create supplier {supplier}")
        return redirect(url_for("supplier.index"))
    return render_template("supplier/form.html", title=_("New Supplier"), form=form)


@supplier_bp.route("/<int:supplier_id>")
@login_required
@shareholder.require(403)
def detail(supplier_id):
    expense_page = request.args.get("expense_page", 1, type=int)
    payed_page = request.args.get("payed_page", 1, type=int)
    unpayed_page = request.args.get("unpayed_page", 1, type=int)
    unpayed_query = db.session.query(Order).filter(
        Order.expense_id.is_(None), Order.supplier_id == supplier_id
    )
    unpay_value = (
        unpayed_query.with_entities(func.coalesce(func.sum(Order.value), 0))
        .filter(not_(Order.expense.has()), Order.supplier_id == supplier_id)
        .first()[0]
    )
    payed_query = (
        db.session.query(Order)
        .filter(Order.expense_id.isnot(None), Order.supplier_id == supplier_id)
        .join(Order.expense)
    )
    payed_value = (
        payed_query.with_entities(func.coalesce(func.sum(Order.value), 0))
        .filter(Order.expense.has(), Order.supplier_id == supplier_id)
        .first()[0]
    )
    return render_template(
        "supplier/detail.html",
        title=_("Supplier Detail"),
        supplier=Supplier.get_or_404(supplier_id),
        expenses=db.session.query(NonLaborExpense)
        .filter(NonLaborExpense.supplier_id == supplier_id)
        .order_by(NonLaborExpense.date.desc())
        .paginate(page=expense_page, per_page=10),
        payed=payed_query.order_by(Expense.date.desc()).paginate(
            page=payed_page, per_page=10
        ),
        unpayed=unpayed_query.order_by(Order.delivery_date.desc()).paginate(
            page=unpayed_page, per_page=10
        ),
        file_form=FileForm(),
        unpay_value=unpay_value,
        payed_value=payed_value,
    )


@supplier_bp.route("/<int:supplier_id>/update", methods=["GET", "POST"])
@login_required
@manager.require(403)
def update(supplier_id):
    supplier = Supplier.get_or_404(supplier_id)
    form = SupplierForm()
    form.hide_id.data = supplier_id
    if form.validate_on_submit():
        supplier.update_by_form(form)
        flash(_('Supplier "%(name)s" has been updated.', name=supplier.name), "success")
        db.session.commit()
        current_app.logger.info(f"Update supplier {supplier}")
        return redirect(url_for("supplier.detail", supplier_id=supplier_id))

    form.process(obj=supplier)

    return render_template(
        "supplier/form.html",
        supplier=supplier,
        form=form,
        title=_("Update Supplier"),
    )


@supplier_bp.route("/<int:supplier_id>/upload", methods=["POST"])
@login_required
@manager.require(403)
def upload(supplier_id):
    form = FileForm()
    file = form.file.data
    if form.validate_on_submit():
        db_file = SupplierFile.create_by_form(form, Supplier.get_or_404(supplier_id))
        flash(
            _('File "%(name)s" has been uploaded.', name=db_file.full_name), "success"
        )
        db.session.commit()
        current_app.logger.info(f"Upload supplier file {db_file}")
        compress_file.queue(db_file.id)

    elif file is not None:
        flash(
            _('Invalid file format "%(format)s".', format=File.split_file_format(file)),
            "danger",
        )
    else:
        flash(_("No file has been uploaded."), "danger")
    return redirect(url_for("supplier.detail", supplier_id=supplier_id))


@supplier_bp.route("/export/<export_format>")
@login_required
@manager.require(403)
def export(export_format):
    current_app.logger.info(f"Export supplier {export_format} file")
    if export_format == "csv":
        return send_file(
            Supplier.export_to_csv(), cache_timeout=0, download_name="Suppliers.csv"
        )
    elif export_format == "excel":
        return send_file(
            Supplier.export_to_excel(), cache_timeout=0, download_name="Suppliers.xlsx"
        )
