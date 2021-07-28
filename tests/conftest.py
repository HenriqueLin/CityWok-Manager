from citywok_ms.expense.models import LaborExpense, NonLaborExpense, SalaryPayment
import datetime
from io import BytesIO
import os
from datetime import date
from tempfile import TemporaryDirectory

import pytest
from citywok_ms import create_app, current_app, db, principal, login
from citywok_ms.auth.models import User
from citywok_ms.employee.models import Employee
from citywok_ms.file.models import (
    EmployeeFile,
    ExpenseFile,
    OrderFile,
    SalaryPaymentFile,
    SupplierFile,
)
from citywok_ms.supplier.models import Supplier
from citywok_ms.order.models import Order
from config import TestConfig
from flask_login import login_user
from flask_principal import Identity
from werkzeug.security import generate_password_hash
from PIL import Image, ImageDraw


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
    )
    session = db.create_scoped_session({"expire_on_commit": False})
    session.add(user)
    session.commit()
    if marker is None or not marker.args[0]:
        user.role = "admin"
    else:
        user.role = marker.args[0]
    session.commit()

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
        accountant_id=1,
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
        iban="PT50123123",
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


@pytest.fixture
def image():
    image = Image.new("RGB", (300, 50))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), "This text is drawn on image")

    byte_io = BytesIO()

    image.save(byte_io, "JPEG")
    byte_io.seek(0)
    return byte_io


@pytest.fixture
def order(supplier):
    order = Order(
        order_number="ORDER-1",
        delivery_date=datetime.date.today(),
        value=123,
        supplier_id=1,
    )
    db.session.add(order)
    db.session.commit()


@pytest.fixture
def order_with_file():
    f = OrderFile(full_name="test_file.txt", order_id=1)
    db.session.add(f)
    db.session.flush()
    with open(
        os.path.join(current_app.config["UPLOAD_FOLDER"], str(f.id) + ".txt"), "x"
    ) as file:
        file.write("test_file")
    f.size = os.path.getsize(f.path)
    db.session.commit()


@pytest.fixture
def expenses(supplier, employee, order):
    labor = LaborExpense(
        date=datetime.datetime.today().date(),
        category="labor:advance",
        cash=150.00,
        employee=Employee.query.get(1),
    )
    db.session.add(labor)
    month = SalaryPayment.get_or_create(datetime.datetime.today().replace(day=1).date())
    salary = LaborExpense(
        date=datetime.datetime.today().date(),
        category="labor:salary",
        cash=150.00,
        employee=Employee.query.get(1),
        month=month,
    )
    db.session.add(salary)
    non_labor = NonLaborExpense(
        date=datetime.datetime.today().date(),
        category="operation:rent",
        cash=150.00,
        supplier=Supplier.query.get(1),
    )
    db.session.add(non_labor)
    order_payment = NonLaborExpense(
        date=datetime.datetime.today().date(),
        category="operation:rent",
        cash=150.00,
        supplier=Supplier.query.get(1),
        orders=[Order.query.get(1)],
    )
    db.session.add(order_payment)
    db.session.commit()


@pytest.fixture
def expense_with_file(expenses):
    f = ExpenseFile(full_name="test_file.txt", expense_id=1)
    db.session.add(f)
    db.session.flush()
    with open(
        os.path.join(current_app.config["UPLOAD_FOLDER"], str(f.id) + ".txt"), "x"
    ) as file:
        file.write("test_file")
    f.size = os.path.getsize(f.path)
    db.session.commit()


@pytest.fixture
def salary_payment_with_file():
    f = SalaryPaymentFile(
        full_name="test_file.txt",
        salary_payment_id=datetime.datetime.today().replace(day=1),
    )
    db.session.add(f)
    db.session.flush()
    with open(
        os.path.join(current_app.config["UPLOAD_FOLDER"], str(f.id) + ".txt"), "x"
    ) as file:
        file.write("test_file")
    f.size = os.path.getsize(f.path)
    db.session.commit()
