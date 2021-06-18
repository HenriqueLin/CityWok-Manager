import datetime
import os
from datetime import date
from tempfile import TemporaryDirectory

import pytest
from citywok_ms import create_app, current_app, db, principal, login
from citywok_ms.auth.models import User
from citywok_ms.employee.models import Employee
from citywok_ms.file.models import EmployeeFile, SupplierFile
from citywok_ms.supplier.models import Supplier
from config import TestConfig
from flask_login import login_user
from flask_principal import Identity
from werkzeug.security import generate_password_hash


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
def user(client, mocker, request):
    marker = request.node.get_closest_marker("role")
    user = User(
        username="user",
        email="user@mail.com",
        password=generate_password_hash("user"),
        role="user",
        confirmed=True,
    )
    db.session.add(user)
    db.session.commit()
    if marker is None or not marker.args[0]:
        user.role = "admin"
    else:
        user.role = marker.args[0]
    db.session.commit()

    if marker is not None and marker.args[0]:
        login_user(user)

        @login.request_loader
        def load_user_from_request(request):
            return user

        @principal.identity_loader
        def load_identity():
            return Identity(user.id)

    yield user

    @login.request_loader
    def load_user_from_request_none(request):
        return None


@pytest.fixture
def app_without_db():
    with TemporaryDirectory() as temp_dir:
        TestConfig.UPLOAD_FOLDER = temp_dir
        app = create_app(config_class=TestConfig)
        with app.app_context():
            yield app


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
