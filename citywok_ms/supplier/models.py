from citywok_ms.utils.models import CRUDMixin
from citywok_ms.file.models import SupplierFile
from typing import List
from citywok_ms import db
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship


class Supplier(db.Model, CRUDMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    abbreviation = Column(String)
    principal = Column(String)
    contact = Column(Integer)
    email = Column(String)
    nif = Column(Integer, unique=True)
    iban = Column(String, unique=True)
    address = Column(String)
    postcode = Column(String)
    city = Column(String)
    remark = Column(Text)

    files = relationship("File")

    def __repr__(self):
        return f"Supplier({self.id}: {self.name})"

    @property
    def active_files(self) -> List[SupplierFile]:
        return (
            db.session.query(SupplierFile)
            .filter(
                SupplierFile.supplier_id == self.id,
                SupplierFile.delete_date.is_(None),
            )
            .all()
        )

    @property
    def deleted_files(self) -> List[SupplierFile]:
        return (
            db.session.query(SupplierFile)
            .filter(
                SupplierFile.supplier_id == self.id,
                SupplierFile.delete_date.isnot(None),
            )
            .all()
        )
