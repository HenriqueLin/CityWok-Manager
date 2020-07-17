import os
from pathlib import Path
from flask import Blueprint, safe_join, render_template, redirect, url_for, current_app, flash, request, send_from_directory, g
from flask_login import login_required

from citywok_manager import db
from citywok_manager.models import Supplier, File
from citywok_manager.supplier.forms import SupplierForm, SupplierFilter, SupplierFileForm

supplier = Blueprint('supplier', __name__, url_prefix="/supplier")


@supplier.route("/", methods=['GET', 'POST'])
@login_required
def index():
    filterForm = SupplierFilter()
    if filterForm.validate_on_submit():
        suppliers = Supplier.query.filter(
            Supplier.name.like(f'%{filterForm.context.data}%')).\
            order_by(getattr(Supplier, filterForm.order.data))
    else:
        suppliers = Supplier.query.all()
    keys = Supplier.get_keys()
    heads = Supplier.get_heads()
    return render_template('supplier/index.html',
                           title='供应商管理',
                           suppliers=suppliers,
                           keys=keys, heads=heads,
                           filterForm=filterForm)


@supplier.route("/new", methods=['GET', 'POST'])
@login_required
def new():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier()
        form.populate_obj(supplier)
        db.session.add(supplier)
        db.session.commit()
        Path(os.path.join(current_app.config['SUPPLIER_FILE'], str(
            supplier.id))).mkdir(exist_ok=True)
        flash('成功添加新供应商', 'success')
        return redirect(url_for('supplier.index'))
    return render_template('supplier/new.html', title='添加供应商', form=form)


@supplier.route("/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def detail(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm()
    form.id.data = supplier_id

    if request.method == "POST":
        # update employee
        if 'update' in request.form and form.validate():
            form.populate_obj(supplier)
            db.session.commit()
            flash('供应商信息已更新', 'success')
            return redirect(url_for('supplier.detail',
                                    supplier_id=supplier_id))

    form.process(obj=supplier)
    return render_template('supplier/detail.html',
                           supplier=supplier,
                           form=form,
                           title='供应商信息信息',
                           heads=File.get_heads(),
                           data=supplier.files)


@supplier.route('/<int:supplier_id>/add_file', methods=['GET', 'POST'])
def add_file(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    g.id = supplier_id
    form = SupplierFileForm()
    if form.validate_on_submit():
        file = form.file.data
        f_name, f_ext = os.path.splitext(file.filename)
        if form.file_name.data:
            f_name = form.file_name.data
        supplier.files.append(File(file_name=f_name, file_ext=f_ext,
                                   file_note=form.file_note.data))
        db.session.commit()
        path = os.path.join(
            current_app.config['SUPPLIER_FILE'], str(supplier_id), f_name + f_ext)
        file.save(path)
        flash('文件添加成功', 'success')
        return redirect(url_for('supplier.detail',
                                supplier_id=supplier_id))
    return render_template('supplier/add_file.html', fileform=form, title='添加文件')


@supplier.route('/<int:supplier_id>/delete_file/<path:filename>', methods=['POST'])
@login_required
def delete_file(supplier_id, filename):
    db.session.delete(File.query.filter_by(
        supplier_id=supplier_id, full_name=filename).first())
    db.session.commit()
    Path(os.path.join(current_app.config['SUPPLIER_FILE'], str(
        supplier_id), filename)).unlink()
    flash('文件成功删除', 'success')
    return redirect(url_for('supplier.detail', supplier_id=supplier_id))


@supplier.route("/<int:supplier_id>/download_file/<path:filename>", methods=['GET'])
@login_required
def get_file(supplier_id, filename):
    path = os.path.join(current_app.config['SUPPLIER_FILE'], str(supplier_id))
    return send_from_directory(path, filename=filename, cache_timeout=0)
