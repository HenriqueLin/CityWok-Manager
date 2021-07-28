from flask_babel import lazy_gettext as _l
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


class Income(db.Model):
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
