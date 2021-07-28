from citywok_ms.file.models import IncomeFile, RevenueFile
from typing import List
from flask_babel import lazy_gettext as _l
from sqlalchemy.ext.hybrid import hybrid_property
from citywok_ms import db
from citywok_ms.utils.models import CRUDMixin, SqliteDecimal
from sqlalchemy import Column, Date, Integer, Text, ForeignKey, String
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship

INCOME = (("revenue", _l("Revenue")), ("other_income", _l("Other Income")))


class Revenue(db.Model):
    date = Column(Date, primary_key=True)
    t_revenue = Column(SqliteDecimal(2), nullable=False)
    remark = Column(Text)
    files = relationship("RevenueFile")

    @property
    def active_files(self) -> List[RevenueFile]:
        return (
            db.session.query(RevenueFile)
            .filter(
                RevenueFile.revenue_id == self.date,
                RevenueFile.delete_date.is_(None),
            )
            .all()
        )

    @property
    def deleted_files(self) -> List[RevenueFile]:
        return (
            db.session.query(RevenueFile)
            .filter(
                RevenueFile.revenue_id == self.date,
                RevenueFile.delete_date.isnot(None),
            )
            .all()
        )


class Income(db.Model, CRUDMixin):
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    category = Column(
        ChoiceType(INCOME),
        nullable=False,
    )
    remark = Column(Text)

    cash = Column(SqliteDecimal(2), default=0)
    check = Column(SqliteDecimal(2), default=0)
    card = Column(SqliteDecimal(2), default=0)
    transfer = Column(SqliteDecimal(2), default=0)

    files = relationship("IncomeFile", cascade="all, delete-orphan")

    @hybrid_property
    def total(self):
        return sum((self.cash, self.card, self.transfer, self.check))

    @hybrid_property
    def non_cash(self):
        return sum((self.card, self.transfer, self.check))

    @property
    def active_files(self) -> List[IncomeFile]:
        return (
            db.session.query(IncomeFile)
            .filter(
                IncomeFile.income_id == self.id,
                IncomeFile.delete_date.is_(None),
            )
            .all()
        )

    @property
    def deleted_files(self) -> List[IncomeFile]:
        return (
            db.session.query(IncomeFile)
            .filter(
                IncomeFile.income_id == self.id,
                IncomeFile.delete_date.isnot(None),
            )
            .all()
        )
