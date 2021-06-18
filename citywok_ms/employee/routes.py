import citywok_ms.employee.messages as employee_msg
import citywok_ms.file.messages as file_msg
from citywok_ms import db
from citywok_ms.auth.permissions import manager, shareholder, visitor
from citywok_ms.employee.forms import EmployeeForm
from citywok_ms.employee.models import Employee
from citywok_ms.file.forms import FileForm
from citywok_ms.file.models import EmployeeFile, File
from flask import Blueprint, flash, redirect, render_template, url_for

employee = Blueprint("employee", __name__, url_prefix="/employee")


@employee.route("/")
@visitor.require(401)
def index():
    return render_template(
        "employee/index.html",
        title=employee_msg.INDEX_TITLE,
        active_employees=Employee.get_active(),
        suspended_employees=Employee.get_suspended(),
    )


@employee.route("/new", methods=["GET", "POST"])
@manager.require(403)
def new():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee.create_by_form(form)
        flash(employee_msg.NEW_SUCCESS.format(name=employee.full_name), "success")
        db.session.commit()
        return redirect(url_for("employee.index"))
    return render_template(
        "employee/form.html", title=employee_msg.NEW_TITLE, form=form
    )


@employee.route("/<int:employee_id>")
@shareholder.require(403)
def detail(employee_id):
    return render_template(
        "employee/detail.html",
        title=employee_msg.DETAIL_TITLE,
        employee=Employee.get_or_404(employee_id),
        file_form=FileForm(),
    )


@employee.route("/<int:employee_id>/update", methods=["GET", "POST"])
@manager.require(403)
def update(employee_id):
    employee = Employee.get_or_404(employee_id)
    form = EmployeeForm()
    form.hide_id.data = employee_id
    if form.validate_on_submit():
        employee.update_by_form(form)
        flash(employee_msg.UPDATE_SUCCESS.format(name=employee.full_name), "success")
        db.session.commit()
        return redirect(url_for("employee.detail", employee_id=employee_id))

    form.process(obj=employee)

    return render_template(
        "employee/form.html",
        employee=employee,
        form=form,
        title=employee_msg.UPDATE_TITLE,
    )


@employee.route("/<int:employee_id>/suspend", methods=["POST"])
@manager.require(403)
def suspend(employee_id):
    employee = Employee.get_or_404(employee_id)
    employee.suspend()
    flash(employee_msg.SUSPEND_SUCCESS.format(name=employee.full_name), "success")
    db.session.commit()
    return redirect(url_for("employee.detail", employee_id=employee_id))


@employee.route("/<int:employee_id>/activate", methods=["POST"])
@manager.require(403)
def activate(employee_id):
    employee = Employee.get_or_404(employee_id)
    employee.activate()
    flash(employee_msg.ACTIVATE_SUCCESS.format(name=employee.full_name), "success")
    db.session.commit()
    return redirect(url_for("employee.detail", employee_id=employee_id))


@employee.route("/<int:employee_id>/upload", methods=["POST"])
@manager.require(403)
def upload(employee_id):
    form = FileForm()
    file = form.file.data
    if form.validate_on_submit():
        db_file = EmployeeFile.create_by_form(form, Employee.get_or_404(employee_id))
        flash(file_msg.UPLOAD_SUCCESS.format(name=db_file.full_name), "success")
        db.session.commit()
    elif file is not None:
        flash(
            file_msg.INVALID_FORMAT.format(format=File.split_file_format(file)),
            "danger",
        )
    else:
        flash(file_msg.NO_FILE, "danger")
    return redirect(url_for("employee.detail", employee_id=employee_id))
