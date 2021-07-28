# from citywok_ms import db
# from citywok_ms.models import Employee, File
# from flask import request

import datetime
import html

import pytest
from citywok_ms import db
from citywok_ms.file.forms import FileForm
from citywok_ms.file.models import (
    EmployeeFile,
    ExpenseFile,
    OrderFile,
    SalaryPaymentFile,
    SupplierFile,
)
from flask import request
from flask.helpers import url_for
from wtforms.fields.simple import HiddenField, SubmitField


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_download_get(client, user, employee_with_file, id):
    response = client.get(
        url_for("file.download", file_id=id),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"test_file" in response.data


def test_download_post(client):
    response = client.post(url_for("file.download", file_id=id))
    assert response.status_code == 405


def test_delete_get(client):
    response = client.get(url_for("file.delete", file_id=id))
    assert response.status_code == 405


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_delete_post(client, user, employee_with_file, id):
    response = client.post(
        url_for("file.delete", file_id=id),
        follow_redirects=True,
    )
    data = response.data.decode()
    f = EmployeeFile.get_or_404(id)

    assert response.status_code == 200
    assert f.delete_date is not None

    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    if id == 1:
        assert f'File "{f.full_name}" has been deleted.' in html.unescape(data)
    elif id == 2:
        assert f'File "{f.full_name}" has already been deleted.' in html.unescape(data)


def test_restore_get(client):
    response = client.get(url_for("file.restore", file_id=id))
    assert response.status_code == 405


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_restore_post(client, user, employee_with_file, id):
    response = client.post(
        url_for("file.restore", file_id=id),
        follow_redirects=True,
    )
    data = response.data.decode()
    f = EmployeeFile.get_or_404(id)

    assert response.status_code == 200
    assert f.delete_date is None

    assert request.url.endswith(url_for("employee.detail", employee_id=id))
    if id == 1:
        assert f'File "{f.full_name}" hasn\'t been deleted.' in html.unescape(data)
    elif id == 2:
        assert f'File "{f.full_name}" has been restored.' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_get_employee_file(client, user, employee_with_file, id):
    response = client.get(url_for("file.update", file_id=id))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Update File" in data
    # form
    for field in FileForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data

    f = EmployeeFile.get_or_404(id)
    assert f.base_name in data
    assert f.format in data
    assert "Update" in data

    # links
    assert url_for("employee.detail", employee_id=id) in data


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_get_supplier_file(client, user, supplier_with_file, id):
    response = client.get(url_for("file.update", file_id=id))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Update File" in data
    # form
    for field in FileForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data

    f = SupplierFile.get_or_404(id)
    assert f.base_name in data
    assert f.format in data
    assert "Update" in data

    # links
    assert url_for("supplier.detail", supplier_id=id) in data


@pytest.mark.role("admin")
def test_update_get_order_file(client, user, order_with_file):
    response = client.get(url_for("file.update", file_id=1))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Update File" in data
    # form
    for field in FileForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data

    f = OrderFile.get_or_404(1)
    assert f.base_name in data
    assert f.format in data
    assert "Update" in data

    # links
    assert url_for("order.detail", order_id=1) in data


@pytest.mark.role("admin")
def test_update_get_expense_file(client, user, expense_with_file):
    response = client.get(url_for("file.update", file_id=1))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Update File" in data
    # form
    for field in FileForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data

    f = ExpenseFile.get_or_404(1)
    assert f.base_name in data
    assert f.format in data
    assert "Update" in data

    # links
    assert url_for("expense.detail", expense_id=1) in data


@pytest.mark.role("admin")
def test_update_get_salary_payment_file(client, user, salary_payment_with_file):
    response = client.get(url_for("file.update", file_id=1))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Update File" in data
    # form
    for field in FileForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data

    f = SalaryPaymentFile.get_or_404(1)
    assert f.base_name in data
    assert f.format in data
    assert "Update" in data

    # links
    assert (
        url_for(
            "expense.salary_index",
            month_str=datetime.datetime.today().strftime("%Y-%m"),
        )
        in data
    )


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_post_valid(client, user, employee_with_file, id):
    request_data = {
        "file_name": "updated",
        "remark": "xxx",
    }
    response = client.post(
        url_for("file.update", file_id=id),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("employee.detail", employee_id=id))

    # database data
    assert db.session.query(EmployeeFile).count() == 2
    f = EmployeeFile.get_or_404(id)

    assert f.remark == "xxx"

    assert f.full_name in data
    assert f.format in data
    assert "Update" in data

    # flash messege
    assert f'File "{f.full_name}" has been updated.' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_post_invalid(client, user, employee_with_file, id):
    response = client.post(
        url_for("file.update", file_id=id),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("file.update", file_id=id))

    assert "This field is required." in data
