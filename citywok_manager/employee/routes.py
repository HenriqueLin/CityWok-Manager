from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, safe_join, send_from_directory
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_

from citywok_manager import db
from citywok_manager.models import Employee, Sex, Id_type, EmployeeFile
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


@employee.route("/<int:employee_id>", methods=['GET', 'POST'])
@login_required
def detail(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm()
    fileform = EmployeeFileForm()
    form.id.data = employee_id

    if request.method == "POST":
        # delete employee
        if 'delete' in request.form:
            employee.is_active = False
            db.session.commit()
            flash('员工成功删除', 'success')
            return redirect(url_for('employee.index'))
        # update employee
        elif 'update' in request.form and form.validate():
            form.populate_obj(employee)
            db.session.commit()
            flash('员工信息已更新', 'success')
            return redirect(url_for('employee.index'))
        # active employee
        elif 'active' in request.form:
            employee.is_active = True
            db.session.commit()
            flash('员工已重新激活', 'success')
            return redirect(url_for('employee.index'))
        # add file
        elif 'add_file' in request.form and fileform.validate():
            file = fileform.file.data
            _, f_ext = os.path.splitext(file.filename)
            new_name = fileform.file_name.data + f_ext
            path = safe_join(current_app.root_path,
                             'download/employee', str(employee_id), new_name)
            file.save(path)
            if not EmployeeFile.query.filter_by(owner_id=employee_id, file_name=new_name).first():
                employee.files.append(EmployeeFile(file_name=new_name,
                                                   note=fileform.note.data))
                db.session.commit()
                flash('文件添加成功', 'success')
            else:
                flash('文件名已存在，请删除原文件后/更改文件名后 重试', 'danger')
            return redirect(url_for('employee.detail',
                                    employee_id=employee_id))

    form.process(obj=employee)
    form.sex.data = employee.sex.name
    form.id_type.data = employee.id_type.name

    return render_template('employee/detail.html',
                           form=form,
                           fileform=fileform,
                           title='员工信息',
                           state=employee.is_active,
                           heads=EmployeeFile.get_heads(),
                           data=employee.files)


@employee.route('/<int:employee_id>/<path:filename>/delete', methods=['GET'])
@login_required
def delete_file(employee_id, filename):
    file = EmployeeFile.query.filter_by(
        owner_id=employee_id, file_name=filename).first()
    db.session.delete(file)
    db.session.commit()
    flash('文件成功删除', 'success')
    return redirect(url_for('employee.detail', employee_id=employee_id))


@employee.route("/employee/new", methods=['GET', 'POST'])
@login_required
def new():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee()
        form.populate_obj(employee)
        db.session.add(employee)
        db.session.commit()
        os.mkdir(safe_join(
            current_app.root_path, 'download/employee', str(employee.id)))
        flash('成功添加新员工', 'success')
        return redirect(url_for('employee.index'))
    return render_template('employee/new.html', title='添加员工', form=form, state=True)


@employee.route("/<int:employee_id>/<path:filename>", methods=['GET'])
def get_file(employee_id, filename):
    folder = safe_join(current_app.root_path, 'download',
                       'employee', str(employee_id))
    return send_from_directory(folder, filename=filename)


@employee.route("/employee/<path:filename>", methods=['GET'])
@login_required
def export(filename):
    employee2excel()
    folder = safe_join(current_app.root_path, 'download', 'employee')
    return send_from_directory(folder, filename=filename, cache_timeout=0)
