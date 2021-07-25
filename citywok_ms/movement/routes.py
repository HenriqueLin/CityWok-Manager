import datetime

from sqlalchemy.sql.elements import not_

from citywok_ms import db
from citywok_ms.employee.models import Employee
from citywok_ms.file.models import ExpenseFile
from citywok_ms.movement.forms import (
    DateForm,
    LaborExpenseForm,
    MonthForm,
    NonLaborExpenseForm,
    OrderPaymentForm,
    SalaryForm,
)
from citywok_ms.movement.models import (
    ROOT,
    Expense,
    LaborExpense,
    NonLaborExpense,
    SalaryPayment,
)
from citywok_ms.order.models import Order
from citywok_ms.task import compress_file
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import _
from sqlalchemy import false, func
from sqlalchemy.orm import with_polymorphic

expense_bp = Blueprint("expense", __name__, url_prefix="/expense")


# Expenses
@expense_bp.route("/", methods=["GET", "POST"])
@expense_bp.route("/<date_str>", methods=["GET", "POST"])
def index(date_str=None):
    if date_str is None:
        return redirect(url_for("expense.index", date_str=datetime.date.today()))

    form = DateForm(date=datetime.datetime.strptime(date_str, "%Y-%m-%d"))
    if form.validate_on_submit():
        return redirect(url_for("expense.index", date_str=form.date.data))
    else:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    expense = with_polymorphic(Expense, "*")
    query = db.session.query(expense).filter(Expense.date == date)
    category_query = (
        query.with_entities(
            func.sum(Expense.total).label("amount"),
            func.substr(
                Expense.category, 1, func.instr(expense.category, ":") - 1
            ).label("root_category"),
        )
        .group_by("root_category")
        .order_by("root_category")
    )
    category_label = [str(dict(ROOT)[x.root_category]) for x in category_query.all()]
    category_value = [str(x.amount) for x in category_query.all()]

    method = query.with_entities(
        func.coalesce(func.sum(Expense.cash), 0).label("cash"),
        func.coalesce(func.sum(Expense.card), 0).label("card"),
        func.coalesce(func.sum(Expense.check), 0).label("check"),
        func.coalesce(func.sum(Expense.transfer), 0).label("transfer"),
    ).first()
    return render_template(
        "movement/expense/index.html",
        title=_("Expenses"),
        form=form,
        category_value=category_value,
        category_label=category_label,
        method=method,
        expenses=query.all(),
    )


@expense_bp.route("/non_labor/new", methods=["GET", "POST"])
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
        return redirect(url_for("expense.index"))
    return render_template(
        "movement/expense/new_non_labor.html",
        title=_("New Non-Labor Expense"),
        form=form,
    )


@expense_bp.route("/labor/new", methods=["GET", "POST"])
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
        return redirect(url_for("expense.index"))
    return render_template(
        "movement/expense/new_labor.html", title=_("New Labor Expense"), form=form
    )


@expense_bp.route("/order_payment/new", methods=["GET", "POST"])
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
            return redirect(url_for("expense.index"))
    else:
        form.orders.query_factory = lambda: db.session.query(false()).filter(false())

    return render_template(
        "movement/expense/new_order_payment.html",
        title=_("New Orders Payment"),
        form=form,
    )


@expense_bp.route("/salary/new/<int:employee_id>/<month_str>", methods=["GET", "POST"])
def new_salary(employee_id, month_str):
    month = datetime.datetime.strptime(month_str, "%Y-%m").date()
    form = SalaryForm()
    employee = Employee.get_or_404(employee_id)
    if employee.payed(month):
        flash(_("Employee already payed at the given month."), "warning")
        return redirect(url_for("expense.salary_index"))
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
        return redirect(url_for("expense.salary_index"))
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


@expense_bp.route("/salary", methods=["GET", "POST"])
@expense_bp.route("/salary/<month_str>", methods=["GET", "POST"])
def salary_index(month_str=None):
    if month_str is None:
        return redirect(
            url_for(
                "expense.salary_index",
                month_str=datetime.datetime.today().strftime("%Y-%m"),
            )
        )
    month = datetime.datetime.strptime(month_str, "%Y-%m").date()
    form = MonthForm(month=month)
    if form.validate_on_submit():
        return redirect(
            url_for("expense.salary_index", month_str=form.month.data.strftime("%Y-%m"))
        )

    payed = db.session.query(Employee, LaborExpense.cash, LaborExpense.non_cash).filter(
        Employee.payed(month),
        LaborExpense.employee_id == Employee.id,
        LaborExpense.month_id == month,
    )
    active = db.session.query(Employee).filter(
        not_(Employee.payed(month)), Employee.active
    )
    return render_template(
        "movement/expense/salary_index.html",
        title=_("Salary Payment"),
        form=form,
        payed=payed.all(),
        active=active.all(),
        month_str=month_str,
    )
