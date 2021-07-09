import io
import os
from citywok_ms.file.models import OrderFile
import html
from citywok_ms.supplier.models import Supplier
from citywok_ms.order.models import Order
import datetime
from flask import url_for, request
import pytest
from wtforms.fields.simple import FileField, HiddenField, SubmitField
from citywok_ms.order.forms import OrderForm
from citywok_ms import db


@pytest.mark.role("admin")
def test_index_get(client, user):
    response = client.get(url_for("order.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Order" in data

    # links
    assert url_for("order.new") in data


@pytest.mark.role("admin")
def test_index_get_with_order(client, user, order):
    response = client.get(url_for("order.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Order" in data

    # links
    assert url_for("order.new") in data
    assert url_for("order.detail", order_id=1) in data

    # datas
    assert "ORDER-1" in data


@pytest.mark.role("admin")
def test_index_post(client, user):
    response = client.post(url_for("order.index"))

    assert response.status_code == 405


@pytest.mark.role("admin")
def test_new_get(client, user):
    response = client.get(url_for("order.new"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "New Order" in data

    # form
    for field in OrderForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data
    assert "Add" in data

    # links
    assert url_for("order.index") in data


@pytest.mark.role("admin")
def test_new_post_valid(client, user, image, supplier):
    request_data = {
        "order_number": "NEW-1",
        "delivery_date": datetime.date.today(),
        "value": 123,
        "supplier": 1,
        "files": (image, "test.jpg"),
    }
    response = client.post(
        url_for("order.new"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("order.index"))

    # database data
    assert db.session.query(Order).count() == 1
    assert len(db.session.query(Supplier).get(1).orders) == 1
    order = db.session.query(Order).first()

    assert order.order_number == request_data["order_number"]
    assert order.delivery_date == request_data["delivery_date"]
    assert order.value == request_data["value"]
    assert order.supplier == db.session.query(Supplier).get(1)

    # flash messege
    assert "New order has been registe." in data


@pytest.mark.role("admin")
def test_new_post_invalid(client, user):
    response = client.post(
        url_for("order.new"),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("order.new"))

    # database data
    assert db.session.query(Order).count() == 0

    assert "This field is required." in data


@pytest.mark.role("admin")
def test_update_get(client, user, order):
    response = client.get(url_for("order.update", order_id=1))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Update Order" in data
    # form
    for field in OrderForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField, FileField)):
            continue
        assert field.id in data

    order = Order.get_or_404(1)
    for attr in Order.__table__.columns:
        if attr.name == "files" or getattr(order, attr.name) is None:
            continue
        assert str(getattr(order, attr.name)) in data
    assert "Update" in data

    # links
    assert url_for("order.detail", order_id=1) in data


@pytest.mark.role("admin")
def test_update_post_valid(client, user, order):
    request_data = {
        "order_number": "UPDATE-1",
        "delivery_date": datetime.date.today(),
        "value": 321,
        "supplier": 1,
    }
    response = client.post(
        url_for("order.update", order_id=1),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("order.detail", order_id=1))

    # database data
    assert db.session.query(Order).count() == 1
    order = Order.get_or_404(1)
    assert order.order_number == request_data["order_number"]
    assert order.delivery_date == request_data["delivery_date"]
    assert order.value == request_data["value"]
    assert order.supplier == db.session.query(Supplier).get(1)

    # flash messege
    assert "Order has been updated." in data


@pytest.mark.role("admin")
def test_update_post_invalid(client, user, order):
    response = client.post(
        url_for("order.update", order_id=1),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("order.update", order_id=1))

    # database data
    assert db.session.query(Order).count() == 1

    assert "Order has been updated." not in data
    assert "This field is required." in data


@pytest.mark.role("admin")
def test_detail_get(client, user, order):
    response = client.get(url_for("order.detail", order_id=1))
    data = response.data.decode()

    order = Order.get_or_404(1)

    # state code
    assert response.status_code == 200
    # titles
    assert "Order Detail" in data
    assert "Files" in data

    # links
    assert url_for("order.update", order_id=1) in data
    assert url_for("order.upload", order_id=1) in data
    assert url_for("order.index") in data
    assert url_for("supplier.detail", supplier_id=order.supplier_id) in data

    # database data
    for attr in Order.__table__.columns:
        if attr.name == "files" or getattr(order, attr.name) is None:
            continue
        assert str(getattr(order, attr.name)) in data

    assert "Deleted Files" in data
    assert "These files will be permanente removed 30 days after being deleted" in data


@pytest.mark.role("admin")
def test_upload_get(client, user, order):
    response = client.get(
        url_for("order.upload", order_id=1),
    )
    assert response.status_code == 405


@pytest.mark.role("admin")
def test_upload_post_valid(client, user, order, image):
    request_data = {
        "file": (image, "test.jpg"),
    }
    response = client.post(
        url_for("order.upload", order_id=1),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()
    assert response.status_code == 200
    assert request.url.endswith(url_for("order.detail", order_id=1))
    assert 'File "test.jpg" has been uploaded.' in html.unescape(data)
    assert db.session.query(OrderFile).count() == 1
    f = db.session.query(OrderFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.role("admin")
def test_upload_post_invalid_format(client, user, order):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.exe"),
    }
    response = client.post(
        url_for("order.upload", order_id=1),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("order.detail", order_id=1))
    assert 'Invalid file format ".exe".' in html.unescape(data)


@pytest.mark.role("admin")
def test_upload_post_invalid_empty(client, user, order):
    response = client.post(
        url_for("order.upload", order_id=1),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("order.detail", order_id=1))
    assert "No file has been uploaded." in html.unescape(data)
