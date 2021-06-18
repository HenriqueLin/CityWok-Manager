from werkzeug.datastructures import FileStorage
from citywok_ms.file.forms import FileForm
import os
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from citywok_ms import db
from flask import current_app, url_for
from humanize import naturalsize
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from citywok_ms.utils.models import CRUDMixin


class File(db.Model, CRUDMixin):
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    upload_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    delete_date = Column(DateTime)
    size = Column(Integer)
    remark = Column(Text)

    type = Column(String)

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "file"}

    def __repr__(self):
        return f"File({self.id}: {self.full_name})"

    @property
    def format(self) -> str:
        return os.path.splitext(self.full_name)[1]

    @hybrid_property
    def base_name(self) -> str:
        return os.path.splitext(self.full_name)[0]

    @base_name.setter
    def base_name(self, new_name: str):
        self.full_name = new_name + self.format

    @property
    def internal_name(self) -> str:
        return f"{self.id}{self.format}"

    @property
    def path(self) -> str:
        return os.path.join(current_app.config["UPLOAD_FOLDER"], self.internal_name)

    @property
    def humanized_size(self) -> str:
        return naturalsize(self.size, format="%.2f")

    def delete(self):
        self.delete_date = datetime.utcnow()

    def restore(self):
        self.delete_date = None

    def update_by_form(self, form: FileForm):
        self.remark = form.remark.data
        self.base_name = form.file_name.data

    @staticmethod
    def split_file_format(file: FileStorage) -> str:
        return os.path.splitext(file.filename)[1]


class EmployeeFile(File):
    employee_id = Column(Integer, ForeignKey("employee.id"))

    __mapper_args__ = {"polymorphic_identity": "employee_file"}

    @property
    def owner_url(self) -> str:
        return url_for("employee.detail", employee_id=self.employee_id, _anchor="Files")

    @staticmethod
    def create_by_form(form: FileForm, owner) -> "File":
        file = form.file.data
        db_file = EmployeeFile(full_name=file.filename, employee_id=owner.id)
        db.session.add(db_file)
        db.session.flush()
        file.save(
            os.path.join(current_app.config["UPLOAD_FOLDER"], db_file.internal_name)
        )
        db_file.size = os.path.getsize(db_file.path)
        return db_file


class SupplierFile(File):
    supplier_id = Column(Integer, ForeignKey("supplier.id"))

    __mapper_args__ = {"polymorphic_identity": "supplier_file"}

    @property
    def owner_url(self) -> str:
        return url_for("supplier.detail", supplier_id=self.supplier_id, _anchor="Files")

    @staticmethod
    def create_by_form(form: FileForm, owner) -> "File":
        file = form.file.data
        db_file = SupplierFile(full_name=file.filename, supplier_id=owner.id)
        db.session.add(db_file)
        db.session.flush()
        file.save(
            os.path.join(current_app.config["UPLOAD_FOLDER"], db_file.internal_name)
        )
        db_file.size = os.path.getsize(db_file.path)
        return db_file
