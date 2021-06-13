import citywok_ms.file.messages as file_msg
import citywok_ms.supplier.messages as supplier_msg
from citywok_ms.auth.permissions import manager, shareholder, visitor
from citywok_ms.file.forms import FileForm
from citywok_ms.file.models import File, SupplierFile
from citywok_ms.supplier.forms import SupplierForm
from citywok_ms.supplier.models import Supplier
from flask import Blueprint, flash, redirect, render_template, url_for

supplier = Blueprint("supplier", __name__, url_prefix="/supplier")


@supplier.route("/")
@visitor.require(401)
def index():
    return render_template(
        "supplier/index.html",
        title=supplier_msg.INDEX_TITLE,
        suppliers=Supplier.get_all(),
    )


@supplier.route("/new", methods=["GET", "POST"])
@manager.require(403)
def new():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier.create_by_form(form)
        flash(supplier_msg.NEW_SUCCESS.format(name=supplier.name), "success")
        return redirect(url_for("supplier.index"))
    return render_template(
        "supplier/form.html", title=supplier_msg.NEW_TITLE, form=form
    )


@supplier.route("/<int:supplier_id>")
@shareholder.require(403)
def detail(supplier_id):
    return render_template(
        "supplier/detail.html",
        title=supplier_msg.DETAIL_TITLE,
        supplier=Supplier.get_or_404(supplier_id),
        file_form=FileForm(),
    )


@supplier.route("/<int:supplier_id>/update", methods=["GET", "POST"])
@manager.require(403)
def update(supplier_id):
    supplier = Supplier.get_or_404(supplier_id)
    form = SupplierForm()
    form.hide_id.data = supplier_id
    if form.validate_on_submit():
        supplier.update_by_form(form)
        flash(supplier_msg.UPDATE_SUCCESS.format(name=supplier.name), "success")
        return redirect(url_for("supplier.detail", supplier_id=supplier_id))

    form.process(obj=supplier)

    return render_template(
        "supplier/form.html",
        supplier=supplier,
        form=form,
        title=supplier_msg.UPDATE_TITLE,
    )


@supplier.route("/<int:supplier_id>/upload", methods=["POST"])
@manager.require(403)
def upload(supplier_id):
    form = FileForm()
    file = form.file.data
    if form.validate_on_submit():
        db_file = SupplierFile.create_by_form(form, Supplier.get_or_404(supplier_id))
        flash(file_msg.UPLOAD_SUCCESS.format(name=db_file.full_name), "success")
    elif file is not None:
        flash(
            file_msg.INVALID_FORMAT.format(format=File.split_file_format(file)),
            "danger",
        )
    else:
        flash(file_msg.NO_FILE, "danger")
    return redirect(url_for("supplier.detail", supplier_id=supplier_id))
