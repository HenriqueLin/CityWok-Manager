import datetime
import html
import io
import os

import pytest
from citywok_ms import db
from citywok_ms.file.models import SupplierFile
from citywok_ms.supplier.forms import SupplierForm
from citywok_ms.supplier.models import Supplier
from flask import request, url_for
from wtforms.fields.simple import HiddenField, SubmitField


@pytest.mark.role("admin")
def test_index_get(client, user):
    response = client.get(url_for("supplier.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Suppliers" in data

    # links
    assert url_for("supplier.new") in data
    assert url_for("supplier.detail", supplier_id=1) not in data


@pytest.mark.role("admin")
def test_index_get_with_supplier(client, user, supplier):
    response = client.get(url_for("supplier.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Suppliers" in data

    # links
    assert url_for("supplier.new") in data
    assert url_for("supplier.detail", supplier_id=1) in data
    assert url_for("supplier.detail", supplier_id=2) in data

    # datas
    assert "BASIC" in data
    assert "FULL" in data


@pytest.mark.role("admin")
def test_index_post(client, user):
    response = client.post(url_for("supplier.index"))

    assert response.status_code == 405


@pytest.mark.role("admin")
def test_new_get(client, user):
    response = client.get(url_for("supplier.new"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "New Supplier" in data

    # form
    for field in SupplierForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data
    assert "Add" in data

    # links
    assert url_for("supplier.index") in data


@pytest.mark.role("admin")
def test_new_post_valid(client, user):
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
    assert f'New supplier "{supplier.name}" has been added.' in html.unescape(data)


@pytest.mark.role("admin")
def test_new_post_invalid(client, user, supplier):
    request_data = {
        "name": "BASIC",
        "nif": "123123",
        "iban": "PT50123123",
    }
    response = client.post(
        url_for("supplier.new"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("supplier.new"))
    # form validation message
    assert "This field is required." in data
    assert "This NIF already existe" in data
    assert "This IBAN already existe" in data

    # database data
    assert db.session.query(Supplier).count() == 2  # 2 supplier from fixture


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])  # id of 2 supplier created in "supplier" fixture
def test_detail_get(client, user, supplier_with_file, id):
    response = client.get(url_for("supplier.detail", supplier_id=id))
    data = response.data.decode()

    # get supplier entity for compar data
    supplier = Supplier.get_or_404(id)

    # state code
    assert response.status_code == 200
    # titles
    assert "Supplier Detail" in data
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


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_get(client, user, supplier, id):
    response = client.get(url_for("supplier.update", supplier_id=id))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Update Supplier" in data
    # form
    for field in SupplierForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data

    supplier = Supplier.get_or_404(id)
    for attr in Supplier.__table__.columns:
        if getattr(supplier, attr.name) is None:
            continue
        assert str(getattr(supplier, attr.name)) in data
    assert "Update" in data

    # links
    assert url_for("supplier.detail", supplier_id=id) in data


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_post_valid(client, user, supplier, id):
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
    assert f'Supplier "{supplier.name}" has been updated.' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_update_post_invalid(client, user, supplier, id):
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


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_upload_get(client, user, supplier, id):
    response = client.get(
        url_for("supplier.upload", supplier_id=id),
    )
    assert response.status_code == 405


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_valid(client, user, supplier, id):
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
    assert 'File "test.jpg" has been uploaded.' in html.unescape(data)
    assert db.session.query(SupplierFile).count() == 1
    f = db.session.query(SupplierFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_invalid_format(client, user, supplier, id):
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
    assert 'Invalid file format ".exe".' in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2])
def test_upload_post_invalid_empty(client, user, supplier, id):
    response = client.post(
        url_for("supplier.upload", supplier_id=id),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("supplier.detail", supplier_id=id))
    assert "No file has been uploaded." in html.unescape(data)
