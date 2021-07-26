from typing import List
from citywok_ms.file.models import ExpenseFile, SalaryPaymentFile
import datetime
from flask_babel import lazy_gettext as _l
from sqlalchemy.orm import relationship
from citywok_ms import db
from citywok_ms.utils.models import CRUDMixin, SqliteDecimal
from sqlalchemy import Column, Date, Integer, Text, ForeignKey, String
from sqlalchemy_utils import ChoiceType
from sqlalchemy.ext.hybrid import hybrid_property

LABOR = (
    ("labor:salary", _l("Salary"), _l("Labor - Salary")),
    ("labor:overtime", _l("Overtime"), _l("Labor - Overtime")),
    ("labor:advance", _l("Advance"), _l("Labor - Advance")),
    ("labor:bonus", _l("Bonus"), _l("Labor - Bonus")),
    ("labor:other", _l("Other"), _l("Labor - Other")),
)
OPERATION = (
    ("operation:rent", _l("Rent"), _l("Operation - Rent")),
    ("operation:water", _l("Water"), _l("Operation - Water")),
    ("operation:electricity", _l("Electricity"), _l("Operation - Electricity")),
    ("operation:gas", _l("Gas"), _l("Operation - Gas")),
    ("operation:communication", _l("Communication"), _l("Operation - Communication")),
    ("operation:fuel", _l("Fuel"), _l("Operation - Fuel")),
    ("operation:bank", _l("Bank"), _l("Operation - Bank")),
    ("operation:server", _l("Server"), _l("Operation - Server")),
    ("operation:other", _l("Other"), _l("Operation - Other")),
)
MATERIAL = (
    ("material:meat", _l("Meat"), _l("Material - Meat")),
    ("material:seafood", _l("SeaFood"), _l("Material - SeaFood")),
    ("material:fruit/veg", _l("Fruit/Vegetable"), _l("Material - Fruit/Vegetable")),
    ("material:frozen", _l("Frozen"), _l("Material - Frozen")),
    ("material:drinks", _l("Drinks"), _l("Material - Others")),
    ("material:chinese_goods", _l("Chinese Goods"), _l("Material - Chinese Goods")),
    ("material:sanitary", _l("Sanitary"), _l("Material - Sanitary")),
    ("material:stationery", _l("Stationery"), _l("Material - Stationery")),
    ("material:other", _l("Other"), _l("Material - Others")),
)
TAX = (
    ("tax:irs", _l("IRS"), _l("Tax - IRS")),
    ("tax:iva", _l("IVA"), _l("Tax - IVA")),
    ("tax:ss", _l("Social Security"), _l("Tax - Social Security")),
    ("tax:iuc", _l("IUC"), _l("Tax - IUC")),
    ("tax:other", _l("Other"), _l("Tax - Other")),
)
ROOT = (
    ("labor", _l("Labor")),
    ("material", _l("Material")),
    ("operation", _l("Operation")),
    ("tax", _l("Tax")),
)


class Expense(db.Model, CRUDMixin):
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    category = Column(
        ChoiceType(tuple((x, y) for x, _, y in (LABOR + OPERATION + MATERIAL + TAX))),
        nullable=False,
    )
    remark = Column(Text)

    cash = Column(SqliteDecimal(2))
    check = Column(SqliteDecimal(2))
    card = Column(SqliteDecimal(2))
    transfer = Column(SqliteDecimal(2))

    files = relationship("ExpenseFile")
    type = Column(String)

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "expense"}

    @hybrid_property
    def total(self):
        return self.cash + self.card + self.transfer + self.check

    @hybrid_property
    def non_cash(self):
        return self.card + self.transfer + self.check

    @property
    def active_files(self) -> List[ExpenseFile]:
        return (
            db.session.query(ExpenseFile)
            .filter(
                ExpenseFile.expense_id == self.id,
                ExpenseFile.delete_date.is_(None),
            )
            .all()
        )

    @property
    def deleted_files(self) -> List[ExpenseFile]:
        return (
            db.session.query(ExpenseFile)
            .filter(
                ExpenseFile.expense_id == self.id,
                ExpenseFile.delete_date.isnot(None),
            )
            .all()
        )


class LaborExpense(Expense):
    id = Column(Integer, ForeignKey("expense.id"), primary_key=True)

    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)
    employee = relationship("Employee", backref="expenses")

    month_id = Column(Date, ForeignKey("salary_payment.month"))

    __mapper_args__ = {
        "polymorphic_identity": "labor_expense",
    }


class NonLaborExpense(Expense):
    id = Column(Integer, ForeignKey("expense.id"), primary_key=True)

    supplier_id = Column(Integer, ForeignKey("supplier.id"), nullable=False)
    supplier = relationship("Supplier", backref="expenses")

    orders = relationship("Order", backref="expense")

    __mapper_args__ = {
        "polymorphic_identity": "non_labor_expense",
    }


class SalaryPayment(db.Model):
    month = Column(Date, primary_key=True)

    expenses = relationship("LaborExpense", backref="month")
    files = relationship("SalaryPaymentFile")

    @classmethod
    def get_or_create(cls, month):
        salary_payment = db.session.query(cls).filter(cls.month == month).first()
        if not salary_payment:
            salary_payment = cls(month=month)
            db.session.add(salary_payment)
        return salary_payment

    @property
    def active_files(self) -> List[SalaryPaymentFile]:
        return (
            db.session.query(SalaryPaymentFile)
            .filter(
                SalaryPaymentFile.salary_payment_id == self.month,
                SalaryPaymentFile.delete_date.is_(None),
            )
            .all()
        )

    @property
    def deleted_files(self) -> List[SalaryPaymentFile]:
        return (
            db.session.query(SalaryPaymentFile)
            .filter(
                SalaryPaymentFile.salary_payment_id == self.month,
                SalaryPaymentFile.delete_date.isnot(None),
            )
            .all()
        )
