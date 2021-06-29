import csv
import io

import pandas as pd
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

    @classmethod
    def export_to_csv(cls) -> io.BytesIO:
        sio = io.StringIO()
        writer = csv.writer(sio)
        writer.writerow(cls.columns_name.values())
        for e in cls.query.all():
            writer.writerow([getattr(e, col) or "-" for col in cls.columns_name.keys()])
        bio = io.BytesIO()
        bio.write(sio.getvalue().encode("utf_8_sig"))
        bio.seek(0)
        return bio

    @classmethod
    def export_to_excel(cls):
        bio = io.BytesIO()
        df = pd.read_sql(db.session.query(cls).statement, db.session.bind)
        df.columns = cls.columns_name.values()
        df.to_excel(bio, index=False)
        bio.seek(0)
        return bio
