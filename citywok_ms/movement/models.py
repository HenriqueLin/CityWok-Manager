from flask_babel import lazy_gettext as _l
from sqlalchemy.orm import relationship
from citywok_ms import db
from citywok_ms.utils.models import CRUDMixin, SqliteDecimal
from sqlalchemy import Column, Date, Integer, Text, ForeignKey, String
from sqlalchemy_utils import ChoiceType

CATEGORY = (
    ("labor", _l("Labor")),
    ("operation", _l("Operation")),
    ("material", _l("Material")),
    ("tax", _l("Tax")),
    ("other", _l("Other")),
)
LABOR_CATEGORY = (
    ("salary", _l("Salary")),
    ("overtime", _l("Overtime")),
    ("advance", _l("Advance")),
    ("bonus", _l("Bonus")),
)


class Expense(db.Model, CRUDMixin):
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(ChoiceType(CATEGORY), nullable=False)
    remark = Column(Text)

    cash = Column(SqliteDecimal(2))
    check = Column(SqliteDecimal(2))
    card = Column(SqliteDecimal(2))
    transfer = Column(SqliteDecimal(2))

    files = relationship("ExpenseFile")
    type = Column(String)

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "expense"}

    @property
    def total(self):
        return self.cash + self.card + self.transfer + self.check


class LaborExpense(Expense):
    id = Column(Integer, ForeignKey("expense.id"), primary_key=True)

    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)
    employee = relationship("Employee", backref="expenses")

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
