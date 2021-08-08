from citywok_ms.file.models import IncomeFile, RevenueFile
from citywok_ms.expense.models import NonLaborExpense
from citywok_ms.income.models import Income, Revenue
import datetime
import html
import io
import os
import pytest
from wtforms.fields.simple import FileField, HiddenField, SubmitField
from citywok_ms import db
from flask import request, url_for
from citywok_ms.income.forms import IncomeForm, RevenueForm


@pytest.mark.role("admin")
def test_index_get(client, user, today):
    response = client.get(url_for("income.index"), follow_redirects=True)
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    assert request.url.endswith(url_for("income.index", date_str=today))

    for txt in (
        "Income",
        "Total Income",
        "Theoretical Revenue",
        "Actual Revenue",
        "Cash",
        "Non-Cash",
        "0.00€",
        url_for("income.new_revenue", date_str=today),
        url_for("income.new_other_income", date_str=today),
    ):
        assert txt in data


@pytest.mark.role("admin")
def test_index_get_with_revenue(client, user, incomes, today):
    response = client.get(url_for("income.index"), follow_redirects=True)
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    assert request.url.endswith(url_for("income.index", date_str=today))

    for txt in (
        "Income",
        "Total Income",
        "Theoretical Revenue",
        "Actual Revenue",
        "Cash",
        "Non-Cash",
        "1000.00€",
        "660.00€",
        url_for("income.new_other_income", date_str=today),
        "Small Expenditure",
    ):
        assert txt in data


@pytest.mark.role("admin")
def test_index_post(client, user, yesterday, today):
    response = client.post(
        url_for("income.index", date_str=today),
        data={"date": yesterday},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert request.url.endswith(url_for("income.index", date_str=yesterday))


@pytest.mark.role("admin")
def test_new_revenue_get(client, user, today):
    response = client.get(url_for("income.new_revenue", date_str=today))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("income.new_revenue", date_str=today))
    assert "New Revenue" in data

    for field in RevenueForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data
    assert "Add" in data

    assert url_for("income.index") in data


@pytest.mark.role("admin")
def test_new_revenue_post_valid(client, user, supplier, image, today):
    request_data = {
        "date": today,
        "t_revenue": 200,
        "cash": 50,
        "cards-0-total": 50,
        "cards-0-actual": 2,
        "cards-1-total": 0,
        "cards-1-actual": 0,
        "cards-2-total": 0,
        "cards-2-actual": 0,
        "files": (image, "test.jpg"),
    }
    response = client.post(
        url_for("income.new_revenue"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("income.index", date_str=today))

    # database data
    assert db.session.query(Revenue).count() == 1
    assert db.session.query(Income).count() == 2
    assert db.session.query(NonLaborExpense).count() == 1
    revenue = db.session.query(Revenue).first()
    assert revenue.t_revenue == 200
    assert revenue.date == today

    # flash messege
    assert "New revenue has been registed." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_revenue_post_invalid(client, user, supplier, image, today, incomes):
    request_data = {
        "date": today,
        "t_revenue": 0,
        "cash": 0,
        "cards-0-total": 1,
        "cards-0-actual": 3,
        "cards-1-total": 0,
        "cards-1-actual": 0,
        "cards-2-total": 0,
        "cards-2-actual": 0,
    }
    response = client.post(
        url_for("income.new_revenue"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("income.new_revenue"))

    assert "Total value must be greater than actual." in html.unescape(data)
    assert f'Revenue of "{today}" already existe.' in html.unescape(data)
    # database data
    assert db.session.query(Revenue).count() == 1
    assert db.session.query(Income).count() == 3
    assert db.session.query(NonLaborExpense).count() == 1


@pytest.mark.role("admin")
def test_new_other_income_get(client, user, today):
    response = client.get(url_for("income.new_other_income", date_str=today))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("income.new_other_income", date_str=today))
    assert "New Income" in data

    for field in IncomeForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField)):
            continue
        assert field.id in data
    assert "Add" in data

    assert url_for("income.index") in data


@pytest.mark.role("admin")
def test_new_other_income_post_valid(client, user, image, today):
    request_data = {
        "date": today,
        "value-card": 5,
        "value-cash": 5,
        "value-transfer": 5,
        "value-check": 5,
        "files": (image, "test.jpg"),
    }
    response = client.post(
        url_for("income.new_other_income"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("income.index", date_str=today))

    # database data
    assert db.session.query(Revenue).count() == 0
    assert db.session.query(Income).count() == 1
    income = db.session.query(Income).first()
    assert income.cash == 5
    assert income.check == 5
    assert income.transfer == 5
    assert income.card == 5
    assert income.date == today

    # flash messege
    assert "New income has been registed." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_other_income_post_invalid(client, user, today):
    response = client.post(
        url_for("income.new_other_income"), data={}, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("income.new_other_income"))

    # database data
    assert db.session.query(Revenue).count() == 0
    assert db.session.query(Income).count() == 0

    # flash messege
    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2, 3])
def test_detail_get(client, user, incomes, id):
    response = client.get(url_for("income.detail", income_id=id))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Income Detail" in data
    assert "Files" in data

    # links
    if db.session.query(Income).get(id).category == "other_income":
        assert url_for("income.update_other_income", income_id=id) in data
        assert url_for("income.delete", income_id=id) in data
    assert url_for("income.upload", income_id=id) in data

    assert "Deleted Files" in data
    assert "These files will be permanente removed 30 days after being deleted" in data


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2, 3])
def test_update_other_income_get(client, user, today, incomes, id):
    response = client.get(
        url_for("income.update_other_income", income_id=id), follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    if db.session.query(Income).get(id).category == "other_income":
        assert request.url.endswith(url_for("income.update_other_income", income_id=id))
        assert "Update Income" in data
        for field in IncomeForm()._fields.values():
            if isinstance(field, (HiddenField, SubmitField, FileField)):
                continue
            assert field.id in data
        assert "Update" in data
        assert url_for("income.index") in data
    else:
        assert request.url.endswith(url_for("income.detail", income_id=id))
        assert "This income can not be updated." in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2, 3])
def test_update_other_income_post_valid(client, user, today, id, incomes):
    request_data = {
        "date": today,
        "value-card": 1,
        "value-cash": 1,
        "value-transfer": 1,
        "value-check": 1,
    }
    response = client.post(
        url_for("income.update_other_income", income_id=id),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("income.detail", income_id=id))

    if db.session.query(Income).get(id).category == "other_income":
        # database data
        income = db.session.query(Income).get(id)
        assert income.cash == 1
        assert income.check == 1
        assert income.transfer == 1
        assert income.card == 1
        assert income.date == today
        # flash messege
        assert "Income has been updated." in html.unescape(data)
    else:
        assert "This income can not be updated." in html.unescape(data)


@pytest.mark.role("admin")
def test_update_other_income_post_invalid(client, user, today, incomes):
    response = client.post(
        url_for("income.update_other_income", income_id=3),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("income.update_other_income", income_id=3))

    # flash messege
    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
@pytest.mark.parametrize("id", [1, 2, 3])
def test_delete_post_valid(client, user, today, id, incomes):
    category = db.session.query(Income).get(id).category
    response = client.post(
        url_for("income.delete", income_id=id),
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request

    if category == "other_income":
        # database data
        assert db.session.query(Income).get(id) is None
        # flash messege
        assert "Income has been deleted." in html.unescape(data)
        assert request.url.endswith(url_for("income.index", date_str=today))
    else:
        assert request.url.endswith(url_for("income.detail", income_id=id))
        assert "This income can not be deleted." in html.unescape(data)


@pytest.mark.role("admin")
def test_upload_post_valid(client, user, incomes, image):
    request_data = {
        "file": (image, "test.jpg"),
    }
    response = client.post(
        url_for("income.upload", income_id=1),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()
    assert response.status_code == 200
    assert request.url.endswith(url_for("income.detail", income_id=1))
    assert 'File "test.jpg" has been uploaded.' in html.unescape(data)
    assert db.session.query(IncomeFile).count() == 1
    f = db.session.query(IncomeFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.role("admin")
def test_upload_post_invalid_format(client, user, incomes):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.exe"),
    }
    response = client.post(
        url_for("income.upload", income_id=1),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("income.detail", income_id=1))
    assert 'Invalid file format ".exe".' in html.unescape(data)


@pytest.mark.role("admin")
def test_upload_post_invalid_empty(client, user, incomes):
    response = client.post(
        url_for("income.upload", income_id=1),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("income.detail", income_id=1))
    assert "No file has been uploaded." in html.unescape(data)


@pytest.mark.role("admin")
def test_revenue_upload_post_valid(client, user, incomes, image, today):
    request_data = {
        "file": (image, "test.jpg"),
    }
    response = client.post(
        url_for("income.revenue_upload", date_str=today),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()
    assert response.status_code == 200
    assert request.url.endswith(url_for("income.index", date_str=today))
    assert 'File "test.jpg" has been uploaded.' in html.unescape(data)
    assert db.session.query(RevenueFile).count() == 1
    f = db.session.query(RevenueFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.role("admin")
def test_revenue_upload_post_invalid_format(client, user, incomes, today):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.exe"),
    }
    response = client.post(
        url_for("income.revenue_upload", date_str=today),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("income.index", date_str=today))
    assert 'Invalid file format ".exe".' in html.unescape(data)


@pytest.mark.role("admin")
def test_revenue_upload_post_invalid_empty(client, user, incomes, today):
    response = client.post(
        url_for("income.revenue_upload", date_str=today),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("income.index", date_str=today))
    assert "No file has been uploaded." in html.unescape(data)
