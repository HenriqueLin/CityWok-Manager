from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, safe_join, send_from_directory, g
from flask_login import login_required, current_user
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_

from citywok_manager import db
from citywok_manager.models import Employee, Sex, Id_type, File
from citywok_manager.employee.forms import EmployeeForm, EmployeeFileForm, EmployeeFilterForm, EmployeeExportForm
from citywok_manager.employee.utils import employee2excel

employee = Blueprint('employee', __name__, url_prefix="/employee")


@employee.route("/", methods=['GET', 'POST'])
@login_required
def index():
    form = EmployeeFilterForm()
    if request.method == "POST":
        if 'search' in request.form:
            sex = Sex[form.sex.data] if form.sex.data else None
            employees = Employee.query.\
                filter(or_(Employee.first_name.like(f'%{form.name.data}%'),
                           Employee.last_name.like(f'%{form.name.data}%'),
                           Employee.zh_name.like(f'%{form.name.data}%'))).\
                filter(or_(not sex, Employee.sex == sex)).\
                filter(or_(not form.job.data, Employee.job == form.job.data)).\
                filter(or_(not form.nationality.data,
                           Employee.nationality == form.nationality.data)).all()
        else:  # elif 'reset' in request.form:
            return redirect(url_for('employee.index'))
    else:
        employees = Employee.query.filter_by(is_active=True).all()
    pass_employees = Employee.query.filter_by(is_active=False).all()
    keys = Employee.get_keys()
    heads = Employee.get_heads()
    return render_template('employee/index.html', title='员工管理', keys=keys, heads=heads, employees=employees, form=form, pass_employees=pass_employees)


@employee.route("/new", methods=['GET', 'POST'])
@login_required
def new():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee()
        form.populate_obj(employee)
        db.session.add(employee)
        db.session.commit()
        Path(os.path.join(current_app.config['EMPLOYEE_FILE'], str(
            employee.id))).mkdir(exist_ok=True)
        flash('成功添加新员工', 'success')
        return redirect(url_for('employee.index'))
    return render_template('employee/new.html', title='添加员工', form=form, state=True)


@employee.route("/<int:employee_id>", methods=['GET', 'POST'])
@login_required
def detail(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm()
    fileform = EmployeeFileForm()
    form.id.data = employee_id

    if form.validate_on_submit():
        form.populate_obj(employee)
        db.session.commit()
        flash('员工信息已更新', 'success')
        return redirect(url_for('employee.index'))

    form.process(obj=employee)
    form.sex.data = employee.sex.name
    form.id_type.data = employee.id_type.name

    return render_template('employee/detail.html',
                           employee=employee,
                           form=form,
                           fileform=fileform,
                           title='员工信息',
                           state=employee.is_active,
                           heads=File.get_heads(),
                           data=employee.files)


@employee.route('/<int:employee_id>/deactivate', methods=['POST'])
def deactivate(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if employee.is_active:
        employee.is_active = False
        db.session.commit()
        flash('员工成功冻结', 'success')
    else:
        flash('员工已处于冻结状态', 'warning')
    return redirect(url_for('employee.index'))


@employee.route('/<int:employee_id>/activate', methods=['POST'])
def activate(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if not employee.is_active:
        employee.is_active = True
        db.session.commit()
        flash('员工成功激活', 'success')
    else:
        flash('员工已处于激活状态', 'warning')
    return redirect(url_for('employee.index'))


@employee.route('/<int:employee_id>/add_file', methods=['GET', 'POST'])
@login_required
def add_file(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    g.id = employee_id
    form = EmployeeFileForm()
    if form.validate_on_submit():
        file = form.file.data
        f_name, f_ext = os.path.splitext(file.filename)
        if form.file_name.data:
            f_name = form.file_name.data
        employee.files.append(File(file_name=f_name, file_ext=f_ext,
                                   file_note=form.file_note.data))
        db.session.commit()
        path = os.path.join(
            current_app.config['EMPLOYEE_FILE'], str(employee_id), f_name + f_ext)
        file.save(path)
        flash('文件添加成功', 'success')
        return redirect(url_for('employee.detail',
                                employee_id=employee_id))
    return render_template('employee/add_file.html', fileform=form, title='添加文件')


@employee.route('/<int:employee_id>/delete_file/<path:filename>', methods=['POST'])
@login_required
def delete_file(employee_id, filename):
    db.session.delete(File.query.filter_by(
        employee_id=employee_id, full_name=filename).first())
    db.session.commit()
    Path(os.path.join(current_app.config['EMPLOYEE_FILE'], str(
        employee_id), filename)).unlink()
    flash('文件成功删除', 'success')
    return redirect(url_for('employee.detail', employee_id=employee_id))


@employee.route("/<int:employee_id>/download_file/<path:filename>", methods=['GET'])
@login_required
def get_file(employee_id, filename):
    path = os.path.join(current_app.config['EMPLOYEE_FILE'], str(employee_id))
    return send_from_directory(path, filename=filename, cache_timeout=0)


@employee.route("/<path:filename>", methods=['GET'])
@login_required
def export(filename):
    employee2excel()
    folder = safe_join(current_app.root_path, 'download', 'employee')
    return send_from_directory(folder, filename=filename, cache_timeout=0)
