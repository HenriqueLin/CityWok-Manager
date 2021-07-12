from citywok_ms.file.models import ExpenseFile
from citywok_ms.movement.models import NonLaborExpense
from citywok_ms.movement.forms import NonLaborExpenseForm
from flask import Blueprint, redirect, render_template, flash, url_for, current_app
from citywok_ms import db
from flask_babel import _
from citywok_ms.task import compress_file

expense_bp = Blueprint("expense", __name__, url_prefix="/expense")


# Expenses
@expense_bp.route("/new/non_labor", methods=["GET", "POST"])
def new_non_labor():
    form = NonLaborExpenseForm()
    if form.validate_on_submit():
        expense = NonLaborExpense(
            description=form.description.data,
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
        flash(_("New expense has been registed."), "success")
        return redirect(url_for("expense.new_non_labor"))
    return render_template(
        "movement/expense/new_non_labor.html", title=_("New Expense"), form=form
    )
