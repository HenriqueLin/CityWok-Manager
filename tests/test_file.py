# from citywok_ms import db
# from citywok_ms.models import Employee, File
# from flask import request

import html

import pytest
from citywok_ms import db
from citywok_ms.file.forms import FileForm
from citywok_ms.file.messages import (
    DELETE_DUPLICATE,
    DELETE_SUCCESS,
    RESTORE_DUPLICATE,
    RESTORE_SUCCESS,
    UPDATE_SUCCESS,
    UPDATE_TITLE,
)
from citywok_ms.file.models import EmployeeFile
from flask import request
from flask.helpers import url_for
from wtforms.fields.simple import HiddenField, SubmitField


@pytest.mark.parametrize("id", [1, 2])
def test_download_get(client, admin, employee_with_file, id):
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


@pytest.mark.parametrize("id", [1, 2])
def test_delete_post(client, admin, employee_with_file, id):
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
        assert DELETE_SUCCESS.format(name=f.full_name) in html.unescape(data)
    elif id == 2:
        assert DELETE_DUPLICATE.format(name=f.full_name) in html.unescape(data)


def test_restore_get(client):
    response = client.get(url_for("file.restore", file_id=id))
    assert response.status_code == 405


@pytest.mark.parametrize("id", [1, 2])
def test_restore_post(client, admin, employee_with_file, id):
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
        assert RESTORE_DUPLICATE.format(name=f.full_name) in html.unescape(data)
    elif id == 2:
        assert RESTORE_SUCCESS.format(name=f.full_name) in html.unescape(data)


@pytest.mark.parametrize("id", [1, 2])
def test_update_get(client, admin, employee_with_file, id):
    response = client.get(url_for("file.update", file_id=id))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert UPDATE_TITLE in data
    # form
    for field in FileForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.label.text in data

    f = EmployeeFile.get_or_404(id)
    assert f.base_name in data
    assert f.format in data
    assert "Update" in data

    # links
    assert url_for("employee.detail", employee_id=id) in data


@pytest.mark.parametrize("id", [1, 2])
def test_update_post_valid(client, admin, employee_with_file, id):
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
    assert UPDATE_SUCCESS.format(name=f.full_name) in html.unescape(data)


@pytest.mark.parametrize("id", [1, 2])
def test_update_post_invalid(client, admin, employee_with_file, id):
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
