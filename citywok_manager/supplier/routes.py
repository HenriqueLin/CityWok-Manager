import os

from flask import Blueprint, safe_join, render_template, redirect, url_for, current_app, flash, request
from flask_login import login_required

from citywok_manager import db
from citywok_manager.models import Supplier
from citywok_manager.supplier.forms import SupplierForm, SupplierFilter

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
        os.mkdir(safe_join(current_app.root_path,
                           'download/supplier', str(supplier.id)))
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
                           form=form,
                           title='供应商信息信息')
