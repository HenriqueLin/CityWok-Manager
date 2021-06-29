from citywok_ms.utils.models import CRUDMixin
from citywok_ms.file.models import SupplierFile
from typing import List
from citywok_ms import db
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from flask_babel import lazy_gettext as _l


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

    columns_name = {
        "id": _l("ID"),
        "name": _l("Company Name"),
        "abbreviation": _l("Abbreviation"),
        "principal": _l("Principal"),
        "contact": _l("Contact"),
        "email": _l("E-mail"),
        "nif": _l("NIF"),
        "iban": _l("IBAN"),
        "address": _l("Address"),
        "postcode": _l("Postcode"),
        "city": _l("City"),
        "remark": _l("Remark"),
    }

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
