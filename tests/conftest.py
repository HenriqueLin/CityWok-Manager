from datetime import date
import datetime
import os

from citywok_ms.employee.models import Employee
from citywok_ms.supplier.models import Supplier
from citywok_ms.file.models import EmployeeFile, SupplierFile
import pytest
from citywok_ms import create_app, db, current_app
from config import TestConfig
from tempfile import TemporaryDirectory


@pytest.fixture
def app():
    with TemporaryDirectory() as temp_dir:
        TestConfig.UPLOAD_FOLDER = temp_dir
        app = create_app(config_class=TestConfig)
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()


@pytest.fixture
def app_without_db():
    with TemporaryDirectory() as temp_dir:
        TestConfig.UPLOAD_FOLDER = temp_dir
        app = create_app(config_class=TestConfig)
        with app.app_context():
            yield app


@pytest.fixture
def basic_employee_data():
    return {
        "first_name": "basic",
        "last_name": "basic",
        "sex": "F",
        "id_type": "passport",
        "id_number": "1",
        "id_validity": "2100-01-01",
        "nationality": "US",
        "total_salary": 1000,
        "taxed_salary": 635.00,
    }


@pytest.fixture
def complete_employee_data():
    return {
        "first_name": "complete",
        "last_name": "complete",
        "zh_name": "中文",
        "sex": "M",
        "birthday": "2020-01-01",
        "contact": "123123123",
        "email": "123@mail.com",
        "id_type": "passport",
        "id_number": "123",
        "id_validity": "2100-01-01",
        "nationality": "US",
        "nif": 123123,
        "niss": 321321,
        "employment_date": "2021-01-01",
        "total_salary": 1000,
        "taxed_salary": 635.00,
        "remark": "REMARK",
    }


@pytest.fixture
def employee():
    employee = Employee(
        first_name="ACTIVE",
        last_name="ACTIVE",
        sex="M",
        id_type="passport",
        id_number="123",
        id_validity=date(2100, 1, 1),
        nationality="US",
        total_salary=1000,
        taxed_salary=635.00,
    )
    db.session.add(employee)
    employee = Employee(
        first_name="SUSPENDED",
        last_name="SUSPENDED",
        zh_name="中文",
        sex="F",
        birthday=date(2000, 1, 1),
        contact="123123123",
        email="123@mail.com",
        id_type="passport",
        id_number="123",
        id_validity=date(2100, 1, 1),
        nationality="US",
        nif=123123,
        niss=321321,
        employment_date=date(2020, 1, 1),
        total_salary="1000",
        taxed_salary="635.00",
        remark="REMARK",
        active=False,
    )
    db.session.add(employee)
    db.session.commit()


@pytest.fixture
def employee_with_file(employee):
    f = EmployeeFile(full_name="test_file.txt", employee_id=1)
    db.session.add(f)
    db.session.flush()
    with open(
        os.path.join(current_app.config["UPLOAD_FOLDER"], str(f.id) + ".txt"), "x"
    ) as file:
        file.write("test_file")
    f.size = os.path.getsize(f.path)

    f = EmployeeFile(full_name="test_file.txt", employee_id=2)
    db.session.add(f)
    db.session.flush()
    with open(
        os.path.join(current_app.config["UPLOAD_FOLDER"], str(f.id) + ".txt"), "x"
    ) as file:
        file.write("test_file")
    f.size = os.path.getsize(f.path)
    f.delete_date = datetime.datetime.now()
    db.session.commit()


@pytest.fixture
def supplier():
    supplier = Supplier(
        name="BASIC",
        principal="basic",
    )
    db.session.add(supplier)
    supplier = Supplier(
        name="FULL",
        abbreviation="f",
        principal="full",
        contact="123123123",
        email="123@mail.com",
        nif="123123",
        iban="PT50123123",
        address="rua A",
        postcode="1234-567",
        city="city",
        remark="REMARK",
    )
    db.session.add(supplier)
    db.session.commit()


@pytest.fixture
def supplier_with_file(supplier):
    f = SupplierFile(full_name="test_file.txt", supplier_id=1)
    db.session.add(f)
    db.session.flush()
    with open(
        os.path.join(current_app.config["UPLOAD_FOLDER"], str(f.id) + ".txt"), "x"
    ) as file:
        file.write("test_file")
    f.size = os.path.getsize(f.path)

    f = SupplierFile(full_name="test_file.txt", supplier_id=2)
    db.session.add(f)
    db.session.flush()
    with open(
        os.path.join(current_app.config["UPLOAD_FOLDER"], str(f.id) + ".txt"), "x"
    ) as file:
        file.write("test_file")
    f.size = os.path.getsize(f.path)
    f.delete_date = datetime.datetime.now()
    db.session.commit()
