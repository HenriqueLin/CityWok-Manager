from citywok_ms.expense.forms import DateForm
import datetime
from citywok_ms import db
from citywok_ms.expense.models import NonLaborExpense
from citywok_ms.file.models import IncomeFile, RevenueFile
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
    url_for,
    request,
)
from flask_babel import _
from flask_babel import lazy_gettext as _l
from sqlalchemy import func

income_bp = Blueprint("income", __name__, url_prefix="/income")


@income_bp.route("/", methods=["GET", "POST"])
@income_bp.route("/<date_str>", methods=["GET", "POST"])
def index(date_str=None):
    if date_str is None:
        return redirect(url_for("income.index", date_str=datetime.date.today()))
    form = DateForm(date=datetime.datetime.strptime(date_str, "%Y-%m-%d").date())
    if form.validate_on_submit():
        return redirect(url_for("income.index", date_str=form.date.data))
    # if not form.is_submitted():
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

    return render_template(
        "income/index.html",
        title=_("Income"),
        form=form,
        incomes=query.all(),
        income=income,
        revenue=revenue,
        actual_revenue=cash + card,
        date_str=date_str,
    )


@income_bp.route("/new/revenue", methods=["GET", "POST"])
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
        return redirect(url_for("expense.index"))
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
        return redirect(url_for("expense.index"))
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
