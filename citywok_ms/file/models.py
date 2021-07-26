import os
from datetime import datetime

from citywok_ms import db
from citywok_ms.file.forms import FileForm
from citywok_ms.utils.models import CRUDMixin
from flask import current_app, url_for
from humanize import naturalsize
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Date
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.datastructures import FileStorage


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


class OrderFile(File):
    order_id = Column(Integer, ForeignKey("order.id"))

    __mapper_args__ = {"polymorphic_identity": "order_file"}

    @property
    def owner_url(self) -> str:
        return url_for("order.detail", order_id=self.order_id, _anchor="Files")

    @staticmethod
    def create(f: FileStorage) -> "File":
        db_file = OrderFile(full_name=f.filename)
        db.session.add(db_file)
        db.session.flush()
        f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], db_file.internal_name))
        db_file.size = os.path.getsize(db_file.path)
        return db_file


class ExpenseFile(File):
    expense_id = Column(Integer, ForeignKey("expense.id"))

    __mapper_args__ = {"polymorphic_identity": "expense_file"}

    @property
    def owner_url(self) -> str:
        return url_for("expense.detail", expense_id=self.expense_id, _anchor="Files")

    @staticmethod
    def create(f: FileStorage) -> "File":
        db_file = ExpenseFile(full_name=f.filename)
        db.session.add(db_file)
        db.session.flush()
        f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], db_file.internal_name))
        db_file.size = os.path.getsize(db_file.path)
        return db_file


class SalaryPaymentFile(File):
    salary_payment_id = Column(Date, ForeignKey("salary_payment.month"))

    __mapper_args__ = {"polymorphic_identity": "salary_payment_file"}

    @property
    def owner_url(self) -> str:
        return url_for(
            "expense.salary_index",
            month_str=self.salary_payment_id.strftime("%Y-%m"),
            _anchor="Files",
        )

    @staticmethod
    def create(f: FileStorage) -> "File":
        db_file = SalaryPaymentFile(full_name=f.filename)
        db.session.add(db_file)
        db.session.flush()
        f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], db_file.internal_name))
        db_file.size = os.path.getsize(db_file.path)
        return db_file
