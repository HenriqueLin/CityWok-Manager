from citywok_ms import db
from citywok_ms.utils.models import CRUDMixin, SqliteDecimal
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship


class Order(db.Model, CRUDMixin):
    id = Column(Integer, primary_key=True)
    order_number = Column(String, nullable=False)
    delivery_date = Column(Date, nullable=False)
    value = Column(SqliteDecimal(2), nullable=False)

    files = relationship("OrderFile")
