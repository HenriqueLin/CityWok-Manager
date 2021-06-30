from citywok_ms.task import compress_file
from flask.globals import current_app
from citywok_ms import db
from citywok_ms.auth.permissions import manager, shareholder, visitor
from citywok_ms.file.forms import FileForm
from citywok_ms.file.models import File, SupplierFile
from citywok_ms.supplier.forms import SupplierForm
from citywok_ms.supplier.models import Supplier
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
    request,
    send_file,
)
from flask_babel import _

supplier_bp = Blueprint("supplier", __name__, url_prefix="/supplier")


@supplier_bp.route("/")
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
@shareholder.require(403)
def detail(supplier_id):
    return render_template(
        "supplier/detail.html",
        title=_("Supplier Detail"),
        supplier=Supplier.get_or_404(supplier_id),
        file_form=FileForm(),
    )


@supplier_bp.route("/<int:supplier_id>/update", methods=["GET", "POST"])
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
@manager.require(403)
def export(export_format):
    if export_format == "csv":
        return send_file(
            Supplier.export_to_csv(), cache_timeout=0, download_name="Suppliers.csv"
        )
    elif export_format == "excel":
        return send_file(
            Supplier.export_to_excel(), cache_timeout=0, download_name="Suppliers.xlsx"
        )
