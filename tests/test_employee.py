from citywok_ms.file.messages import INVALID_FORMAT, NO_FILE, UPLOAD_SUCCESS
import os
from citywok_ms.file.models import EmployeeFile
import io
from wtforms.fields.simple import HiddenField, SubmitField
from citywok_ms.employee.messages import (
    ACTIVATE_SUCCESS,
    DETAIL_TITLE,
    INDEX_TITLE,
    NEW_SUCCESS,
    NEW_TITLE,
    SUSPEND_SUCCESS,
    UPDATE_SUCCESS,
    UPDATE_TITLE,
)
from citywok_ms.employee.models import Employee
from citywok_ms.employee.forms import EmployeeForm
from citywok_ms import db
import datetime
from flask import url_for, request
import pytest
import html


def test_index_get(client, admin):
    response = client.get(url_for("employee.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert INDEX_TITLE in data
    assert "Active Employees" in data
    assert "Suspended Employees" not in data

    # links
    assert url_for("employee.new") in data
    assert url_for("employee.detail", employee_id=1) not in data


def test_index_get_with_employee(client, admin, employee):
    response = client.get(url_for("employee.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert INDEX_TITLE in data
    assert "Active Employees" in data
    assert "Suspended Employees" in data

    # links
    assert url_for("employee.new") in data
    assert url_for("employee.detail", employee_id=1) in data
    assert url_for("employee.detail", employee_id=2) in data

    # datas
    assert "SUSPENDED" in data
    assert "ACTIVE" in data


def test_index_post(client, admin):
    response = client.post(url_for("employee.index"))

    assert response.status_code == 405


def test_new_get(client, admin):
    response = client.get(url_for("employee.new"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert NEW_TITLE in data

    # form
    for field in EmployeeForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.label.text in data
    assert "Add" in data

    # links
    assert url_for("employee.index") in data


def test_new_post_valid(client, admin):
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
    assert NEW_SUCCESS.format(name=employee.full_name) in html.unescape(data)


def test_new_post_invalid(client, admin):
    response = client.post(url_for("employee.new"), data={}, follow_redirects=True)
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("employee.new"))
    # form validation message
    assert "This field is required." in data

    # database data
    assert db.session.query(Employee).count() == 0


@pytest.mark.parametrize("id", [1, 2])  # id of 2 employee created in "employee" fixture
def test_detail_get(client, admin, employee_with_file, id):
    response = client.get(url_for("employee.detail", employee_id=id))
    data = response.data.decode()

    # get employee entity for compar data
    employee = Employee.get_or_404(id)

    # state code
    assert response.status_code == 200
    # titles
    assert DETAIL_TITLE in data
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


@pytest.mark.parametrize("id", [1, 2])
def test_update_get(client, admin, employee, id):
    response = client.get(url_for("employee.update", employee_id=id))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert UPDATE_TITLE in data
    # form
    for field in EmployeeForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.label.text in data

    employee = Employee.get_or_404(id)
    for attr in Employee.__table__.columns:
        if attr.name == "active" or getattr(employee, attr.name) is None:
            continue
        assert str(getattr(employee, attr.name)) in data
    assert "Update" in data

    # links
    assert url_for("employee.detail", employee_id=id) in data


@pytest.mark.parametrize("id", [1, 2])
def test_update_post_valid(client, admin, employee, id):
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
    assert UPDATE_SUCCESS.format(name=employee.full_name) in html.unescape(data)


@pytest.mark.parametrize("id", [1, 2])
def test_update_post_invalid(client, admin, employee, id):
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


@pytest.mark.parametrize("id", [1, 2])
def test_activate_get(client, admin, employee, id):
    response = client.get(
        url_for("employee.activate", employee_id=id),
    )
    assert response.status_code == 405


@pytest.mark.parametrize("id", [1, 2])
def test_activate_post(client, admin, employee, id):
    response = client.post(
        url_for("employee.activate", employee_id=id),
        follow_redirects=True,
    )
    data = response.data.decode()
    employee = Employee.get_or_404(id)

    assert response.status_code == 200
    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    assert employee.active
    assert ACTIVATE_SUCCESS.format(name=employee.full_name) in html.unescape(data)


@pytest.mark.parametrize("id", [1, 2])
def test_suspende_get(client, admin, employee, id):
    response = client.get(
        url_for("employee.suspend", employee_id=id),
    )
    assert response.status_code == 405


@pytest.mark.parametrize("id", [1, 2])
def test_suspende_post(client, admin, employee, id):
    response = client.post(
        url_for("employee.suspend", employee_id=id),
        follow_redirects=True,
    )
    data = response.data.decode()
    employee = Employee.get_or_404(id)

    assert response.status_code == 200
    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    assert not employee.active
    assert SUSPEND_SUCCESS.format(name=employee.full_name) in html.unescape(data)


@pytest.mark.parametrize("id", [1, 2])
def test_upload_get(client, admin, employee, id):
    response = client.get(
        url_for("employee.upload", employee_id=id),
    )
    assert response.status_code == 405


@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_valid(client, admin, employee, id):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.jpg"),
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
    assert UPLOAD_SUCCESS.format(name="test.jpg") in html.unescape(data)
    assert db.session.query(EmployeeFile).count() == 1
    f = db.session.query(EmployeeFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_invalid_format(client, admin, employee, id):
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
    assert INVALID_FORMAT.format(format=".exe") in html.unescape(data)


@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_invalid_empty(client, admin, employee, id):
    response = client.post(
        url_for("employee.upload", employee_id=id),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    assert NO_FILE in html.unescape(data)
