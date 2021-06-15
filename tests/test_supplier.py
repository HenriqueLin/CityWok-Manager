import datetime
import html
import io
import os

import pytest
from citywok_ms import db
from citywok_ms.file.messages import INVALID_FORMAT, NO_FILE, UPLOAD_SUCCESS
from citywok_ms.file.models import SupplierFile
from citywok_ms.supplier.forms import SupplierForm
from citywok_ms.supplier.messages import (
    DETAIL_TITLE,
    INDEX_TITLE,
    NEW_SUCCESS,
    NEW_TITLE,
    UPDATE_SUCCESS,
    UPDATE_TITLE,
)
from citywok_ms.supplier.models import Supplier
from flask import request, url_for
from wtforms.fields.simple import HiddenField, SubmitField


def test_index_get(client, admin):
    response = client.get(url_for("supplier.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert INDEX_TITLE in data

    # links
    assert url_for("supplier.new") in data
    assert url_for("supplier.detail", supplier_id=1) not in data


def test_index_get_with_supplier(client, admin, supplier):
    response = client.get(url_for("supplier.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert INDEX_TITLE in data

    # links
    assert url_for("supplier.new") in data
    assert url_for("supplier.detail", supplier_id=1) in data
    assert url_for("supplier.detail", supplier_id=2) in data

    # datas
    assert "BASIC" in data
    assert "FULL" in data


def test_index_post(client, admin):
    response = client.post(url_for("supplier.index"))

    assert response.status_code == 405


def test_new_get(client, admin):
    response = client.get(url_for("supplier.new"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert NEW_TITLE in data

    # form
    for field in SupplierForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.label.text in data
    assert "Add" in data

    # links
    assert url_for("supplier.index") in data


def test_new_post_valid(client, admin):
    # new supplier's data
    request_data = {
        "name": "BASIC",
        "principal": "basic",
    }
    response = client.post(
        url_for("supplier.new"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("supplier.index"))

    # database data
    assert db.session.query(Supplier).count() == 1
    supplier = db.session.query(Supplier).first()
    for key in request_data.keys():
        if isinstance(getattr(supplier, key), datetime.date):
            assert getattr(supplier, key).isoformat() == request_data[key]
        else:
            assert getattr(supplier, key) == request_data[key]

    # flash messege
    assert NEW_SUCCESS.format(name=supplier.name) in html.unescape(data)


def test_new_post_invalid(client, admin):
    response = client.post(url_for("supplier.new"), data={}, follow_redirects=True)
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("supplier.new"))
    # form validation message
    assert "This field is required." in data

    # database data
    assert db.session.query(Supplier).count() == 0


@pytest.mark.parametrize("id", [1, 2])  # id of 2 supplier created in "supplier" fixture
def test_detail_get(client, admin, supplier_with_file, id):
    response = client.get(url_for("supplier.detail", supplier_id=id))
    data = response.data.decode()

    # get supplier entity for compar data
    supplier = Supplier.get_or_404(id)

    # state code
    assert response.status_code == 200
    # titles
    assert DETAIL_TITLE in data
    assert "Files" in data

    # links
    assert url_for("supplier.update", supplier_id=id) in data
    assert url_for("supplier.upload", supplier_id=id) in data
    assert url_for("supplier.index") in data

    # database data
    for attr in Supplier.__table__.columns:
        if getattr(supplier, attr.name) is None:
            continue
        assert str(getattr(supplier, attr.name)) in data

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
def test_update_get(client, admin, supplier, id):
    response = client.get(url_for("supplier.update", supplier_id=id))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert UPDATE_TITLE in data
    # form
    for field in SupplierForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.label.text in data

    supplier = Supplier.get_or_404(id)
    for attr in Supplier.__table__.columns:
        if getattr(supplier, attr.name) is None:
            continue
        assert str(getattr(supplier, attr.name)) in data
    assert "Update" in data

    # links
    assert url_for("supplier.detail", supplier_id=id) in data


@pytest.mark.parametrize("id", [1, 2])
def test_update_post_valid(client, admin, supplier, id):
    request_data = {
        "name": "UPDATED",
        "principal": "UPDATED",
    }
    response = client.post(
        url_for("supplier.update", supplier_id=id),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("supplier.detail", supplier_id=id))

    # database data
    assert db.session.query(Supplier).count() == 2
    supplier = Supplier.get_or_404(id)
    for key in request_data.keys():
        if isinstance(getattr(supplier, key), datetime.date):
            assert getattr(supplier, key).isoformat() == request_data[key]
        else:
            assert getattr(supplier, key) == request_data[key]

    # flash messege
    assert UPDATE_SUCCESS.format(name=supplier.name) in html.unescape(data)


@pytest.mark.parametrize("id", [1, 2])
def test_update_post_invalid(client, admin, supplier, id):
    response = client.post(
        url_for("supplier.update", supplier_id=id),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("supplier.update", supplier_id=id))

    # database data
    assert db.session.query(Supplier).filter(Supplier.name == "UPDATED").count() == 0
    assert "This field is required." in data


@pytest.mark.parametrize("id", [1, 2])
def test_upload_get(client, admin, supplier, id):
    response = client.get(
        url_for("supplier.upload", supplier_id=id),
    )
    assert response.status_code == 405


@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_valid(client, admin, supplier, id):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.jpg"),
    }
    response = client.post(
        url_for("supplier.upload", supplier_id=id),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("supplier.detail", supplier_id=id))
    assert UPLOAD_SUCCESS.format(name="test.jpg") in html.unescape(data)
    assert db.session.query(SupplierFile).count() == 1
    f = db.session.query(SupplierFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_invalid_format(client, admin, supplier, id):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.exe"),
    }
    response = client.post(
        url_for("supplier.upload", supplier_id=id),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("supplier.detail", supplier_id=id))
    assert INVALID_FORMAT.format(format=".exe") in html.unescape(data)


@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_invalid_empty(client, admin, supplier, id):
    response = client.post(
        url_for("supplier.upload", supplier_id=id),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("supplier.detail", supplier_id=id))
    assert NO_FILE in html.unescape(data)
