from citywok_ms import db
from citywok_ms.auth.permissions import manager, shareholder, visitor
from citywok_ms.employee.forms import EmployeeForm
from citywok_ms.employee.models import Employee
from citywok_ms.file.forms import FileForm
from citywok_ms.file.models import EmployeeFile, File
from citywok_ms.tasks import compress_file
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_babel import _

employee_bp = Blueprint("employee", __name__, url_prefix="/employee")


@employee_bp.route("/")
@visitor.require(401)
def index():
    return render_template(
        "employee/index.html",
        title=_("Employees"),
        active_employees=Employee.get_active(),
        suspended_employees=Employee.get_suspended(),
    )


@employee_bp.route("/new", methods=["GET", "POST"])
@manager.require(403)
def new():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee.create_by_form(form)
        flash(
            _('New employee "%(name)s" has been added.', name=employee.full_name),
            "success",
        )
        db.session.commit()
        current_app.logger.info(f"Create employee {employee}")
        return redirect(url_for("employee.index"))
    return render_template("employee/form.html", title=_("New Employee"), form=form)


@employee_bp.route("/<int:employee_id>")
@shareholder.require(403)
def detail(employee_id):
    return render_template(
        "employee/detail.html",
        title=_("Employee Detail"),
        employee=Employee.get_or_404(employee_id),
        file_form=FileForm(),
    )


@employee_bp.route("/<int:employee_id>/update", methods=["GET", "POST"])
@manager.require(403)
def update(employee_id):
    employee = Employee.get_or_404(employee_id)
    form = EmployeeForm()
    form.hide_id.data = employee_id
    if form.validate_on_submit():
        employee.update_by_form(form)
        flash(
            _('Employee "%(name)s" has been updated.', name=employee.full_name),
            "success",
        )
        db.session.commit()
        current_app.logger.info(f"Update employee {employee}")
        return redirect(url_for("employee.detail", employee_id=employee_id))

    form.process(obj=employee)

    return render_template(
        "employee/form.html",
        employee=employee,
        form=form,
        title=_("Update Employee"),
    )


@employee_bp.route("/<int:employee_id>/suspend", methods=["POST"])
@manager.require(403)
def suspend(employee_id):
    employee = Employee.get_or_404(employee_id)
    employee.suspend()
    flash(
        _('Employee "%(name)s" has been suspended.', name=employee.full_name), "success"
    )
    db.session.commit()
    current_app.logger.info(f"Suspend employee {employee}")
    return redirect(url_for("employee.detail", employee_id=employee_id))


@employee_bp.route("/<int:employee_id>/activate", methods=["POST"])
@manager.require(403)
def activate(employee_id):
    employee = Employee.get_or_404(employee_id)
    employee.activate()
    flash(
        _('Employee "%(name)s" has been activated.', name=employee.full_name), "success"
    )
    db.session.commit()
    current_app.logger.info(f"Activate employee {employee}")
    return redirect(url_for("employee.detail", employee_id=employee_id))


@employee_bp.route("/<int:employee_id>/upload", methods=["POST"])
@manager.require(403)
def upload(employee_id):
    form = FileForm()
    file = form.file.data
    if form.validate_on_submit():
        db_file = EmployeeFile.create_by_form(form, Employee.get_or_404(employee_id))
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
    return redirect(url_for("employee.detail", employee_id=employee_id))
