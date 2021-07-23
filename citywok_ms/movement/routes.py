import datetime

from citywok_ms import db
from citywok_ms.employee.models import Employee
from citywok_ms.file.models import ExpenseFile
from citywok_ms.movement.forms import (LaborExpenseForm, MonthForm,
                                       NonLaborExpenseForm, OrderPaymentForm,
                                       SalaryForm)
from citywok_ms.movement.models import (LaborExpense, NonLaborExpense,
                                        SalaryPayment)
from citywok_ms.order.models import Order
from citywok_ms.task import compress_file
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import _
from sqlalchemy import false

expense_bp = Blueprint("expense", __name__, url_prefix="/expense")


# Expenses
@expense_bp.route("/new/non_labor", methods=["GET", "POST"])
def new_non_labor():
    form = NonLaborExpenseForm()
    if form.validate_on_submit():
        expense = NonLaborExpense(
            date=form.date.data,
            category=form.category.data,
            remark=form.remark.data,
            supplier=form.supplier.data,
            cash=form.value.cash.data,
            transfer=form.value.transfer.data,
            card=form.value.card.data,
            check=form.value.check.data,
        )
        for f in form.files.data:
            db_file = ExpenseFile.create(f)
            expense.files.append(db_file)
            compress_file.queue(db_file.id)
        db.session.add(expense)
        db.session.commit()
        flash(_("New non-labor expense has been registed."), "success")
        return redirect(url_for("expense.new_non_labor"))
    return render_template(
        "movement/expense/new_non_labor.html",
        title=_("New Non-Labor Expense"),
        form=form,
    )


@expense_bp.route("/new/labor", methods=["GET", "POST"])
def new_labor():
    form = LaborExpenseForm()
    if form.validate_on_submit():
        expense = LaborExpense(
            date=form.date.data,
            category=form.category.data,
            remark=form.remark.data,
            employee=form.employee.data,
            cash=form.value.cash.data,
            transfer=form.value.transfer.data,
            card=form.value.card.data,
            check=form.value.check.data,
        )
        for f in form.files.data:
            db_file = ExpenseFile.create(f)
            expense.files.append(db_file)
            compress_file.queue(db_file.id)
        db.session.add(expense)
        db.session.commit()
        flash(_("New labor expense has been registed."), "success")
        return redirect(url_for("expense.new_labor"))
    return render_template(
        "movement/expense/new_labor.html", title=_("New Labor Expense"), form=form
    )


@expense_bp.route("/new/order_payment", methods=["GET", "POST"])
def new_order_payment():
    form = OrderPaymentForm()
    if form.is_submitted():
        if form.supplier.validate(form):
            form.orders.query_factory = (
                lambda: db.session.query(Order)
                .filter(
                    Order.supplier_id == form.supplier.data.id,
                    Order.expense_id.is_(None),
                )
                .order_by(Order.delivery_date)
            )
        else:
            form.orders.query_factory = lambda: db.session.query(false()).filter(
                false()
            )
        if "submit" in request.form and form.validate():
            expense = NonLaborExpense(
                date=form.date.data,
                category=form.category.data,
                remark=form.remark.data,
                supplier=form.supplier.data,
                orders=form.orders.data,
                cash=form.value.cash.data,
                transfer=form.value.transfer.data,
                card=form.value.card.data,
                check=form.value.check.data,
            )
            for f in form.files.data:
                db_file = ExpenseFile.create(f)
                expense.files.append(db_file)
                compress_file.queue(db_file.id)
            db.session.add(expense)
            db.session.commit()
            flash(_("New labor expense has been registed."), "success")
            return redirect(url_for("expense.new_labor"))
    else:
        form.orders.query_factory = lambda: db.session.query(false()).filter(false())

    return render_template(
        "movement/expense/new_order_payment.html",
        title=_("New Orders Payment"),
        form=form,
    )


@expense_bp.route("/new/salary/<int:employee_id>/<month_str>", methods=["GET", "POST"])
def new_salary(employee_id, month_str):
    month = datetime.datetime.strptime(month_str, "%Y-%m").date()
    form = SalaryForm()
    employee = Employee.get_or_404(employee_id)
    if employee.payed(month):
        flash(_("Employee already payed at the given month."), "warning")
        return redirect(url_for("main.index"))  # FIXME:
    if form.validate_on_submit():
        salary_payment = SalaryPayment.get_or_create(month)
        expense = LaborExpense(
            date=form.date.data,
            category="labor:salary",
            remark=form.remark.data,
            employee=employee,
            cash=form.value.cash.data,
            transfer=form.value.transfer.data,
            card=form.value.card.data,
            check=form.value.check.data,
        )
        for f in form.files.data:
            db_file = ExpenseFile.create(f)
            expense.files.append(db_file)
            compress_file.queue(db_file.id)
        db.session.add(expense)
        salary_payment.expenses.append(expense)
        db.session.commit()
        flash(_("New salary has been registed."), "success")
        return redirect(url_for("expense.new_labor"))
    return render_template(
        "movement/expense/new_salary.html",
        title=_("New Salary"),
        form=form,
        employee=employee,
        month=month,
        last_payments=db.session.query(LaborExpense)
        .filter(LaborExpense.employee_id == employee_id)
        .order_by(LaborExpense.date)
        .limit(10)
        .all(),
    )

