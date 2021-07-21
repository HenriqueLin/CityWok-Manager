from citywok_ms.order.models import Order
from citywok_ms.file.models import ExpenseFile
from citywok_ms.movement.models import LaborExpense, NonLaborExpense
from citywok_ms.movement.forms import (
    LaborExpenseForm,
    NonLaborExpenseForm,
    OrderPaymentForm,
)
from flask import (
    Blueprint,
    redirect,
    render_template,
    flash,
    url_for,
    request,
)
from citywok_ms import db
from flask_babel import _
from citywok_ms.task import compress_file
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
