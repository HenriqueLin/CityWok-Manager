from typing import List
from citywok_ms.file.models import OrderFile
from citywok_ms import db
from citywok_ms.utils.models import CRUDMixin, SqliteDecimal
from sqlalchemy import Column, Date, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship


class Order(db.Model, CRUDMixin):
    id = Column(Integer, primary_key=True)
    order_number = Column(String, nullable=False)
    delivery_date = Column(Date, nullable=False)
    value = Column(SqliteDecimal(2), nullable=False)
    remark = Column(Text)

    supplier_id = Column(Integer, ForeignKey("supplier.id"), nullable=False)
    expense_id = Column(Integer, ForeignKey("expense.id"))
    files = relationship("OrderFile")

    @property
    def active_files(self) -> List[OrderFile]:
        return (
            db.session.query(OrderFile)
            .filter(
                OrderFile.order_id == self.id,
                OrderFile.delete_date.is_(None),
            )
            .all()
        )

    @property
    def deleted_files(self) -> List[OrderFile]:
        return (
            db.session.query(OrderFile)
            .filter(
                OrderFile.order_id == self.id,
                OrderFile.delete_date.isnot(None),
            )
            .all()
        )
