import datetime

from flask_login.utils import login_required

from citywok_ms import db
from citywok_ms.auth.permissions import manager, shareholder
from citywok_ms.expense.forms import DateForm
from citywok_ms.expense.models import Expense, NonLaborExpense
from citywok_ms.file.forms import FileForm
from citywok_ms.file.models import File, IncomeFile, RevenueFile
from citywok_ms.income.forms import IncomeForm, RevenueForm
from citywok_ms.income.models import Income, Revenue
from citywok_ms.supplier.models import Supplier
from citywok_ms.task import compress_file
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_babel import _
from flask_babel import lazy_gettext as _l
from sqlalchemy import func
from sqlalchemy.orm.util import with_polymorphic

income_bp = Blueprint("income", __name__, url_prefix="/income")


@income_bp.route("/", methods=["GET", "POST"])
@income_bp.route("/<date_str>", methods=["GET", "POST"])
@login_required
@shareholder.require(403)
def index(date_str=None):
    if date_str is None:
        return redirect(url_for("income.index", date_str=datetime.date.today()))
    expense_page = request.args.get("expense_page", 1, type=int)
    income_page = request.args.get("income_page", 1, type=int)

    form = DateForm(date=datetime.datetime.strptime(date_str, "%Y-%m-%d").date())
    if form.validate_on_submit():
        return redirect(url_for("income.index", date_str=form.date.data))
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    query = db.session.query(Income).filter(Income.date == date)
    income = query.with_entities(
        func.coalesce(func.sum(Income.total), 0).label("total"),
        func.coalesce(func.sum(Income.cash), 0).label("cash"),
        func.coalesce(func.sum(Income.non_cash), 0).label("non_cash"),
    ).first()
    revenue = db.session.query(Revenue).get(date)
    cash, card = (
        query.with_entities(
            func.coalesce(func.sum(Income.cash), 0),
            func.coalesce(func.sum(Income.card), 0),
        )
        .filter(Income.category == "revenue")
        .first()
    )
    polymorphic = with_polymorphic(Expense, "*")
    expense = db.session.query(polymorphic).filter(
        Expense.from_pos, Expense.date == date
    )
    small_expense = expense.with_entities(
        func.coalesce(func.sum(Expense.total), 0)
    ).first()[0]

    return render_template(
        "income/index.html",
        title=_("Income"),
        form=form,
        incomes=query.paginate(page=income_page, per_page=10),
        income=income,
        revenue=revenue,
        actual_revenue=cash + card + small_expense,
        date_str=date_str,
        expenses=expense.paginate(page=expense_page, per_page=10),
        file_form=FileForm(),
    )


@income_bp.route("/new/revenue", methods=["GET", "POST"])
@login_required
@manager.require(403)
def new_revenue():
    form = RevenueForm()
    if form.validate_on_submit():
        date = form.date.data
        revenue = Revenue(date=date, t_revenue=form.t_revenue.data)
        db.session.add(revenue)
        if form.cash.data > 0:
            cash = Income(date=date, category="revenue", cash=form.cash.data)
            db.session.add(cash)
        for subform in form.cards:
            if subform.total.data > 0:
                card = Income(date=date, category="revenue", card=subform.total.data)
                db.session.add(card)
        if form.cards_fee > 0:
            fee = NonLaborExpense(
                date=date,
                category="operation:bank",
                supplier=Supplier.bank(),
                transfer=form.cards_fee,
            )
            db.session.add(fee)
        for f in form.files.data:
            db_file = RevenueFile.create(f)
            revenue.files.append(db_file)
            compress_file.queue(db_file.id)
        flash(_("New revenue has been registed."), "success")
        db.session.commit()
        current_app.logger.info(f"Create revenue {revenue}")
        return redirect(url_for("income.index", date_str=form.date.data))
    if not form.is_submitted():
        date_str = request.args.get("date_str", None, type=str)
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        if date:
            form.date.data = date
    return render_template(
        "income/revenue.html",
        title=_("New Revenue"),
        form=form,
    )


@income_bp.route("/new/other_income", methods=["GET", "POST"])
@login_required
@manager.require(403)
def new_other_income():
    form = IncomeForm()
    if form.validate_on_submit():
        income = Income(
            date=form.date.data,
            category="other_income",
            cash=form.value.cash.data,
            transfer=form.value.transfer.data,
            card=form.value.card.data,
            check=form.value.check.data,
            remark=form.remark.data,
        )
        db.session.add(income)
        for f in form.files.data:
            db_file = IncomeFile.create(f)
            income.files.append(db_file)
            compress_file.queue(db_file.id)
        flash(_("New income has been registed."), "success")
        db.session.commit()
        current_app.logger.info(f"Create income {income}")
        return redirect(url_for("income.index"))
    if not form.is_submitted():
        date_str = request.args.get("date_str", None, type=str)
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        if date:
            form.date.data = date
    return render_template(
        "income/other_income.html",
        title=_("New Income"),
        form=form,
    )


@income_bp.route("/<int:income_id>")
@login_required
@shareholder.require(403)
def detail(income_id):
    income = Income.get_or_404(income_id)
    return render_template(
        "income/detail.html",
        title=_("Income Detail"),
        file_form=FileForm(),
        income=income,
    )


@income_bp.route("/update/<int:income_id>", methods=["GET", "POST"])
@login_required
@manager.require(403)
def update_other_income(income_id):
    income = Income.get_or_404(income_id)
    if income.category == "revenue":
        flash(_("This income can not be updated."), "danger")
        return redirect(url_for("income.detail", income_id=income_id))
    form = IncomeForm()
    del form.files
    if form.validate_on_submit():
        income.date = form.date.data
        income.remark = form.remark.data
        income.cash = form.value.cash.data
        income.transfer = form.value.transfer.data
        income.card = form.value.card.data
        income.check = form.value.check.data
        flash(_("Income has been updated."), "success")
        db.session.commit()
        current_app.logger.info(f"Update income {income}")
        return redirect(url_for("income.detail", income_id=income_id))
    if not form.is_submitted():
        form.process(obj=income)
        form.value.cash.data = income.cash
        form.value.transfer.data = income.transfer
        form.value.card.data = income.card
        form.value.check.data = income.check
    return render_template(
        "income/other_income.html",
        title=_("Update Income"),
        form=form,
        income_id=income_id,
    )


@income_bp.route("delete/<int:income_id>", methods=["POST"])
@login_required
@manager.require(403)
def delete(income_id):
    income = Income.get_or_404(income_id)
    if income.category == "revenue":
        flash(_("This income can not be deleted."), "danger")
        return redirect(url_for("income.detail", income_id=income_id))
    db.session.delete(income)
    flash(_("Income has been deleted."), "success")
    db.session.commit()
    current_app.logger.info(f"Delete income {income}")
    return redirect(url_for("income.index"))


@income_bp.route("/<int:income_id>/upload", methods=["POST"])
@login_required
@manager.require(403)
def upload(income_id):
    form = FileForm()
    file = form.file.data
    if form.validate_on_submit():
        db_file = IncomeFile.create(form.file.data)
        db_file.income_id = income_id
        flash(
            _('File "%(name)s" has been uploaded.', name=db_file.full_name), "success"
        )
        db.session.commit()
        current_app.logger.info(f"Upload income file {db_file}")
        compress_file.queue(db_file.id)

    elif file is not None:
        flash(
            _('Invalid file format "%(format)s".', format=File.split_file_format(file)),
            "danger",
        )
    else:
        flash(_("No file has been uploaded."), "danger")
    return redirect(url_for("income.detail", income_id=income_id))


@income_bp.route("/revenue/<date_str>/upload", methods=["POST"])
@login_required
@manager.require(403)
def revenue_upload(date_str):
    form = FileForm()
    file = form.file.data
    if form.validate_on_submit():
        db_file = RevenueFile.create(form.file.data)
        db_file.revenue_id = date_str
        flash(
            _('File "%(name)s" has been uploaded.', name=db_file.full_name), "success"
        )
        db.session.commit()
        current_app.logger.info(f"Upload revenue file {db_file}")
        compress_file.queue(db_file.id)

    elif file is not None:
        flash(
            _('Invalid file format "%(format)s".', format=File.split_file_format(file)),
            "danger",
        )
    else:
        flash(_("No file has been uploaded."), "danger")
    return redirect(url_for("income.index", date_str=date_str))
