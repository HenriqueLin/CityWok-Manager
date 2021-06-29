from citywok_ms.file.models import EmployeeFile
from typing import List
from citywok_ms import db
from citywok_ms.utils import ID, SEX
from citywok_ms.utils.models import CRUDMixin, SqliteDecimal
from sqlalchemy import Boolean, Column, Date, Integer, String, Text
from sqlalchemy.sql.expression import nullslast
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from sqlalchemy_utils import ChoiceType, CountryType


class Employee(db.Model, CRUDMixin):
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    zh_name = Column(String)
    accountant_id = Column(Integer, unique=True)
    sex = Column(ChoiceType(SEX, String()), nullable=False)
    birthday = Column(Date)
    contact = Column(String)
    email = Column(String)
    id_type = Column(ChoiceType(ID), nullable=False)
    id_number = Column(String, nullable=False)
    id_validity = Column(Date, nullable=False)
    nationality = Column(CountryType, nullable=False)
    nif = Column(Integer, unique=True)
    niss = Column(Integer, unique=True)
    iban = Column(String, unique=True)
    employment_date = Column(Date)
    total_salary = Column(SqliteDecimal(2))
    taxed_salary = Column(SqliteDecimal(2))
    remark = Column(Text)
    active = Column(Boolean, default=True)

    files = relationship("EmployeeFile")

    def __repr__(self):
        return f"Employee({self.id}: {self.full_name})"

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @validates("sex")
    def validate_sex(self, key, sex):
        if sex not in [s[0] for s in SEX]:  # test: no cover
            raise ValueError(f'"{sex}" not in SEX set')
        else:
            return sex

    @staticmethod
    def get_active(sort, desc) -> List["Employee"]:
        result = db.session.query(Employee).filter_by(active=True)
        if desc:
            result = result.order_by(nullslast(getattr(Employee, sort).desc())).all()
        else:
            result = result.order_by(nullslast(getattr(Employee, sort))).all()
        return result

    @staticmethod
    def get_suspended(sort, desc) -> List["Employee"]:
        result = db.session.query(Employee).filter_by(active=False)
        if desc:
            result = result.order_by(nullslast(getattr(Employee, sort).desc())).all()
        else:
            result = result.order_by(nullslast(getattr(Employee, sort))).all()
        return result

    def activate(self):
        self.active = True

    def suspend(self):
        self.active = False

    @property
    def active_files(self) -> List[EmployeeFile]:
        return (
            db.session.query(EmployeeFile)
            .filter(
                EmployeeFile.employee_id == self.id,
                EmployeeFile.delete_date.is_(None),
            )
            .all()
        )

    @property
    def deleted_files(self) -> List[EmployeeFile]:
        return (
            db.session.query(EmployeeFile)
            .filter(
                EmployeeFile.employee_id == self.id,
                EmployeeFile.delete_date.isnot(None),
            )
            .all()
        )
