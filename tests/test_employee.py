import datetime
import html
import io
import os

import pytest
from citywok_ms import db
from citywok_ms.employee.forms import EmployeeForm
from citywok_ms.employee.models import Employee
from citywok_ms.file.models import EmployeeFile
from flask import request, url_for
from wtforms.fields.simple import HiddenField, SubmitField
import pandas as pd


@pytest.mark.role("admin")
def test_index_get(client, user):
    response = client.get(url_for("employee.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Employees" in data
    assert "Active Employees" in data
    assert "Suspended Employees" not in data

    # links
    assert url_for("employee.new") in data
    assert url_for("employee.detail", employee_id=1) not in data


@pytest.mark.role("admin")
def test_index_get_with_employee(client, user, employee):
    response = client.get(url_for("employee.index", desc=True))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Employees" in data
    assert "Active Employees" in data
    assert "Suspended Employees" in data

    # links
    assert url_for("employee.new") in data
    assert url_for("employee.detail", employee_id=1) in data
    assert url_for("employee.detail", employee_id=2) in data

    # datas
    assert "SUSPENDED" in data
    assert "ACTIVE" in data


@pytest.mark.role("admin")
def test_index_post(client, user):
    response = client.post(url_for("employee.index"))

    assert response.status_code == 405


@pytest.mark.role("admin")
def test_new_get(client, user):
    response = client.get(url_for("employee.new"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "New Employee" in data

    # form
    for field in EmployeeForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data
    assert "Add" in data

    # links
    assert url_for("employee.index") in data


@pytest.mark.role("admin")
def test_new_post_valid(client, user):
    # new employee's data
    request_data = {
        "first_name": "NEW",
        "last_name": "NEW",
        "sex": "F",
        "id_type": "passport",
        "id_number": "1",
        "id_validity": "2100-01-01",
        "nationality": "US",
        "total_salary": 1000,
        "taxed_salary": 635.00,
    }
    response = client.post(
        url_for("employee.new"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("employee.index"))

    # database data
    assert db.session.query(Employee).count() == 1
    employee = db.session.query(Employee).first()
    for key in request_data.keys():
        if isinstance(getattr(employee, key), datetime.date):
            assert getattr(employee, key).isoformat() == request_data[key]
        else:
            assert getattr(employee, key) == request_data[key]

    # flash messege
    assert f'New employee "{employee.full_name}" has been added.' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.role("admin")
def test_new_post_invalid(client, user, employee):
    request_data = {
        "first_name": "NEW",
        "sex": "F",
        "accountant_id": 1,
        "id_type": "passport",
        "id_number": "1",
        "id_validity": "2000-01-01",
        "nationality": "US",
        "total_salary": 1000,
        "taxed_salary": 635.00,
        "nif": 123123,
        "niss": 321321,
        "iban": "PT50123123",
    }
    response = client.post(
        url_for("employee.new"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("employee.new"))
    # form validation message
    assert "This field is required." in data
    assert "ID has expired" in data
    assert "This NIF already existe" in data
    assert "This NISS already existe" in data
    assert "This IBAN already existe" in data
    assert "This Accountant ID already existe" in data

    # database data
    assert db.session.query(Employee).count() == 2  # 2 employee created in fixture


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])  # id of 2 employee created in "employee" fixture
def test_detail_get(client, user, employee_with_file, id):
    response = client.get(url_for("employee.detail", employee_id=id))
    data = response.data.decode()

    # get employee entity for compar data
    employee = Employee.get_or_404(id)

    # state code
    assert response.status_code == 200
    # titles
    assert "Employee Detail" in data
    assert "Files" in data
    if id == 2:
        assert "Suspended" in data

    # links
    assert url_for("employee.update", employee_id=id) in data
    assert url_for("employee.upload", employee_id=id) in data
    assert url_for("employee.index") in data

    # database data
    for attr in Employee.__table__.columns:
        if attr.name == "active" or getattr(employee, attr.name) is None:
            continue
        assert str(getattr(employee, attr.name)) in data

    # files
    assert "test_file" in data
    if id == 1:
        assert url_for("file.download", file_id=1) in data
        assert url_for("file.update", file_id=1) in data
        assert url_for("file.delete", file_id=1) in data
        assert url_for("file.restore", file_id=2) not in data
    elif id == 2:
        assert url_for("file.update", file_id=1) not in data
        assert url_for("file.delete", file_id=1) not in data
        assert url_for("file.download", file_id=2) in data
        assert url_for("file.restore", file_id=2) in data

    assert "Deleted Files" in data
    assert "These files will be permanente removed 30 days after being deleted" in data


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_get(client, user, employee, id):
    response = client.get(url_for("employee.update", employee_id=id))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Update Employee" in data
    # form
    for field in EmployeeForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data

    employee = Employee.get_or_404(id)
    for attr in Employee.__table__.columns:
        if attr.name == "active" or getattr(employee, attr.name) is None:
            continue
        assert str(getattr(employee, attr.name)) in data
    assert "Update" in data

    # links
    assert url_for("employee.detail", employee_id=id) in data


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_post_valid(client, user, employee, id):
    request_data = {
        "first_name": "UPDATED",
        "last_name": "UPDATED",
        "sex": "M",
        "id_type": "id_card",
        "id_number": "321",
        "id_validity": "2100-01-01",
        "nationality": "CN",
        "total_salary": 1200,
        "taxed_salary": 700.00,
    }
    response = client.post(
        url_for("employee.update", employee_id=id),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("employee.detail", employee_id=id))

    # database data
    assert db.session.query(Employee).count() == 2
    employee = Employee.get_or_404(id)
    for key in request_data.keys():
        if isinstance(getattr(employee, key), datetime.date):
            assert getattr(employee, key).isoformat() == request_data[key]
        else:
            assert getattr(employee, key) == request_data[key]

    # flash messege
    assert f'Employee "{employee.full_name}" has been updated.' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_post_invalid(client, user, employee, id):
    response = client.post(
        url_for("employee.update", employee_id=id),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("employee.update", employee_id=id))

    # database data
    assert (
        db.session.query(Employee).filter(Employee.first_name == "UPDATED").count() == 0
    )
    assert "This field is required." in data


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_activate_get(client, user, employee, id):
    response = client.get(
        url_for("employee.activate", employee_id=id),
    )
    assert response.status_code == 405


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_activate_post(client, user, employee, id):
    response = client.post(
        url_for("employee.activate", employee_id=id),
        follow_redirects=True,
    )
    data = response.data.decode()
    employee = Employee.get_or_404(id)

    assert response.status_code == 200
    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    assert employee.active
    assert f'Employee "{employee.full_name}" has been activated.' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_suspende_get(client, user, employee, id):
    response = client.get(
        url_for("employee.suspend", employee_id=id),
    )
    assert response.status_code == 405


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_suspende_post(client, user, employee, id):
    response = client.post(
        url_for("employee.suspend", employee_id=id),
        follow_redirects=True,
    )
    data = response.data.decode()
    employee = Employee.get_or_404(id)

    assert response.status_code == 200
    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    assert not employee.active
    assert f'Employee "{employee.full_name}" has been suspended.' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_upload_get(client, user, employee, id):
    response = client.get(
        url_for("employee.upload", employee_id=id),
    )
    assert response.status_code == 405


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_valid(client, user, employee, id, image):
    request_data = {
        "file": (image, "test.jpg"),
    }
    response = client.post(
        url_for("employee.upload", employee_id=id),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()
    assert response.status_code == 200
    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    assert 'File "test.jpg" has been uploaded.' in html.unescape(data)
    assert db.session.query(EmployeeFile).count() == 1
    f = db.session.query(EmployeeFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_invalid_format(client, user, employee, id):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.exe"),
    }
    response = client.post(
        url_for("employee.upload", employee_id=id),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    assert 'Invalid file format ".exe".' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_invalid_empty(client, user, employee, id):
    response = client.post(
        url_for("employee.upload", employee_id=id),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    assert "No file has been uploaded." in html.unescape(data)


@pytest.mark.role("admin")
def test_export_csv(client, user, employee):
    response = client.get(
        url_for("employee.export", export_format="csv"),
        follow_redirects=True,
    )
    data = response.data.decode()
    assert response.status_code == 200
    for name in Employee.columns_name.values():
        assert str(name) in data
    for employee in Employee.get_all():
        for attr in Employee.__table__.columns:
            assert str(getattr(employee, attr.name) or "-") in data


@pytest.mark.role("admin")
def test_export_excel(client, user, employee):
    response = client.get(
        url_for("employee.export", export_format="excel"),
        follow_redirects=True,
    )
    data = pd.read_excel(response.data)
    assert response.status_code == 200
    for name in Employee.columns_name.values():
        assert str(name) in data

    for employee in Employee.get_all():
        for attr in ("first_name", "last_name", "id"):
            value = getattr(employee, attr)
            assert value in data.values
