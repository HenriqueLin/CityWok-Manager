import datetime
import html
import io
import os

import pytest
from citywok_ms import db
from citywok_ms.expense.forms import NonLaborExpenseForm
from citywok_ms.expense.models import (
    Expense,
    LaborExpense,
    NonLaborExpense,
    SalaryPayment,
)
from citywok_ms.file.models import ExpenseFile, SalaryPaymentFile
from flask import request, url_for
from sqlalchemy.sql.elements import not_
from wtforms.fields.simple import BooleanField, FileField, HiddenField, SubmitField


@pytest.mark.role("admin")
def test_index_get(client, user, expenses, today):
    response = client.get(url_for("expense.index"), follow_redirects=True)
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    assert request.url.endswith(url_for("expense.index", date_str=today))

    for txt in (
        "Expenses",
        "Cash",
        "Total",
        "Non-Cash",
        "600.00€",
        "0.00€",
        url_for("expense.new_non_labor"),
        url_for("expense.new_labor"),
        url_for("expense.new_order_payment"),
        url_for("expense.salary_index"),
        "Category",
        "Payment method",
    ):
        assert txt in data

    for ex in db.session.query(Expense.id).all():
        assert str(ex.id) in data
        assert url_for("expense.detail", expense_id=ex.id) in data


@pytest.mark.role("admin")
def test_index_post(client, user, yesterday, today):
    response = client.post(
        url_for("expense.index", date_str=today),
        data={"date": yesterday},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert request.url.endswith(url_for("expense.index", date_str=yesterday))


@pytest.mark.role("admin")
def test_new_non_labor_get(client, user, supplier):
    response = client.get(url_for("expense.new_non_labor", supplier_id=1))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("expense.new_non_labor", supplier_id=1))
    assert "New Non-Labor Expense" in data

    for field in NonLaborExpenseForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField, BooleanField)):
            continue
        assert field.id in data
    assert "Add" in data

    assert url_for("expense.index") in data


@pytest.mark.role("admin")
def test_new_non_labor_post_valid(client, user, supplier, image, today):
    request_data = {
        "date": today,
        "category": "operation:water",
        "supplier": 1,
        "value-cash": 5,
        "value-card": 5,
        "value-check": 5,
        "value-transfer": 5,
        "files": (image, "test.jpg"),
    }
    response = client.post(
        url_for("expense.new_non_labor"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("expense.index", date_str=today))

    # database data
    assert db.session.query(Expense).count() == 1
    expense = db.session.query(NonLaborExpense).first()
    assert expense.total == 20
    assert expense.date == today
    assert expense.supplier_id == 1
    assert expense.category == "operation:water"
    assert len(expense.files) == 1

    # flash messege
    assert "New non-labor expense has been registed." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_non_labor_post_invalid(client, user):
    response = client.post(
        url_for("expense.new_non_labor"), data={}, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("expense.new_non_labor"))

    # database data
    assert db.session.query(Expense).count() == 0

    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_labor_get(client, user, employee):
    response = client.get(url_for("expense.new_labor", employee_id=1))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("expense.new_labor", employee_id=1))
    assert "New Labor Expense" in data

    for field in NonLaborExpenseForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField, BooleanField)):
            continue
        assert field.id in data
    assert "Add" in data

    assert url_for("expense.index") in data


@pytest.mark.role("admin")
def test_new_labor_post_valid(client, user, employee, image, today):
    request_data = {
        "date": today,
        "category": "labor:advance",
        "employee": 1,
        "value-cash": 5,
        "value-card": 5,
        "value-check": 5,
        "value-transfer": 5,
        "files": (image, "test.jpg"),
    }
    response = client.post(
        url_for("expense.new_labor"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("expense.index", date_str=today))

    # database data
    assert db.session.query(Expense).count() == 1
    expense = db.session.query(LaborExpense).first()
    assert expense.total == 20
    assert expense.date == today
    assert expense.employee_id == 1
    assert expense.category == "labor:advance"
    assert len(expense.files) == 1

    # flash messege
    assert "New labor expense has been registed." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_labor_post_invalid(client, user):
    response = client.post(url_for("expense.new_labor"), data={}, follow_redirects=True)
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("expense.new_labor"))

    # database data
    assert db.session.query(Expense).count() == 0

    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_order_payment_get(client, user, supplier):
    response = client.get(url_for("expense.new_order_payment", supplier_id=1))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("expense.new_order_payment", supplier_id=1))
    assert "New Orders Payment" in data

    for field in NonLaborExpenseForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField, BooleanField)):
            continue
        assert field.id in data
    assert "Add" in data

    assert url_for("expense.index") in data


@pytest.mark.role("admin")
def test_new_order_payment_post_valid(client, user, supplier, image, order, today):
    request_data = {
        "date": today,
        "category": "material:meat",
        "supplier": 1,
        "orders": 1,
        "value-cash": 5,
        "value-card": 5,
        "value-check": 5,
        "value-transfer": 5,
        "files": (image, "test.jpg"),
        "submit": "Add",
    }
    response = client.post(
        url_for("expense.new_order_payment"), data=request_data, follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("expense.index", date_str=today))

    # database data
    assert db.session.query(Expense).count() == 1
    expense = db.session.query(NonLaborExpense).first()
    assert expense.total == 20
    assert expense.date == today
    assert expense.supplier_id == 1
    assert expense.orders[0].id == 1
    assert expense.category == "material:meat"
    assert len(expense.files) == 1

    # flash messege
    assert "New order payment has been registed." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_order_payment_post_invalid(client, user):
    response = client.post(
        url_for("expense.new_order_payment"),
        data={"submit": "Add"},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("expense.new_order_payment"))

    # database data
    assert db.session.query(Expense).count() == 0

    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_salary_get(client, user, employee):
    month_str = datetime.datetime.today().strftime("%Y-%m")
    response = client.get(
        url_for("expense.new_salary", month_str=month_str, employee_id=1)
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(
        url_for("expense.new_salary", month_str=month_str, employee_id=1)
    )
    assert "New Salary" in data
    assert "Employee's Information" in data
    assert "Last Payments" in data
    assert "Payment" in data

    for field in NonLaborExpenseForm()._fields.values():
        if (
            isinstance(field, (HiddenField, SubmitField, BooleanField))
            or field.id == "category"
        ):
            continue
        assert field.id in data
    assert "Add" in data

    assert url_for("employee.detail", employee_id=1) in data
    assert url_for("expense.salary_index") in data


@pytest.mark.role("admin")
def test_new_salary_post_valid(client, user, employee, image, today, current_month):
    request_data = {
        "date": today,
        "value-cash": 5,
        "value-card": 5,
        "value-check": 5,
        "value-transfer": 5,
        "files": (image, "test.jpg"),
    }
    response = client.post(
        url_for("expense.new_salary", month_str=current_month, employee_id=1),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(
        url_for("expense.salary_index", month_str=current_month)
    )

    # database data
    assert db.session.query(Expense).count() == 1
    assert db.session.query(SalaryPayment).count() == 1
    expense = db.session.query(LaborExpense).first()
    assert expense.total == 20
    assert expense.date == today
    assert expense.employee_id == 1
    assert expense.category == "labor:salary"
    assert expense.month_id == today.replace(day=1)
    assert len(expense.files) == 1

    # flash messege
    assert "New salary has been registed." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_salary_post_invalid(client, user, employee, current_month):
    response = client.post(
        url_for("expense.new_salary", month_str=current_month, employee_id=1),
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(
        url_for("expense.new_salary", month_str=current_month, employee_id=1)
    )

    # database data
    assert db.session.query(Expense).count() == 0

    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
def test_new_salary_payed(client, user, expenses, current_month):
    response = client.get(
        url_for("expense.new_salary", month_str=current_month, employee_id=1),
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert "Employee already payed at the given month." in data
    assert request.url.endswith(
        url_for("expense.salary_index", month_str=current_month)
    )


@pytest.mark.role("admin")
def test_salary_index_get(client, user, expenses, current_month):
    response = client.get(url_for("expense.salary_index"), follow_redirects=True)
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    assert request.url.endswith(
        url_for("expense.salary_index", month_str=current_month)
    )

    for txt in (
        "Salary Payment",
        "Cash",
        "Total",
        "Non-Cash",
        "0.00€",
        "Payed",
        "Unpayed",
    ):
        assert txt in data


@pytest.mark.role("admin")
def test_salary_index_post(client, user, last_month):
    response = client.post(
        url_for("expense.salary_index", month_str=last_month),
        data={"month": last_month},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert request.url.endswith(url_for("expense.salary_index", month_str=last_month))


@pytest.mark.role("admin")
def test_detail_get(client, user, expenses):
    response = client.get(url_for("expense.detail", expense_id=1))
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # titles
    assert "Expense Detail" in data
    assert "Files" in data

    # links
    assert url_for("expense.update", expense_id=1) in data
    assert url_for("expense.upload", expense_id=1) in data
    assert url_for("expense.delete", expense_id=1) in data

    assert "Deleted Files" in data
    assert "These files will be permanente removed 30 days after being deleted" in data


@pytest.mark.role("admin")
def test_detail_get_invalid(client, user, expenses):
    response = client.get(url_for("expense.detail", expense_id=0))
    assert response.status_code == 404


@pytest.mark.role("admin")
def test_update_get_invalid(client, user, expenses):
    response = client.get(url_for("expense.update", expense_id=0))
    assert response.status_code == 404


@pytest.mark.role("admin")
def test_update_non_labor_get(client, user, expenses):
    expense = NonLaborExpense.query.filter(not_(NonLaborExpense.orders)).first()
    response = client.get(
        url_for("expense.update", expense_id=expense.id), follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(
        url_for("expense.update_non_labor", expense_id=expense.id)
    )
    assert "Update Non-Labor Expense" in data

    for field in NonLaborExpenseForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField, BooleanField, FileField)):
            continue
        assert field.id in data
    assert "Update" in data

    assert url_for("expense.detail", expense_id=expense.id) in data


@pytest.mark.role("admin")
def test_update_non_labor_post_valid(client, user, expenses, image, today):
    expense = NonLaborExpense.query.filter(not_(NonLaborExpense.orders)).first()
    request_data = {
        "date": today,
        "category": "operation:gas",
        "supplier": 1,
        "value-cash": 10,
        "value-card": 10,
        "value-check": 10,
        "value-transfer": 10,
    }
    response = client.post(
        url_for("expense.update_non_labor", expense_id=expense.id),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert url_for("expense.detail", expense_id=expense.id) in data

    # database data
    assert db.session.query(Expense).count() == 4
    expense = NonLaborExpense.query.filter(not_(NonLaborExpense.orders)).first()
    assert expense.total == 40
    assert expense.date == today
    assert expense.supplier_id == 1
    assert expense.category == "operation:gas"

    # flash messege
    assert "Non-labor expense has been updated." in html.unescape(data)


@pytest.mark.role("admin")
def test_update_non_labor_post_invalid(client, user, expenses):
    expense = NonLaborExpense.query.filter(not_(NonLaborExpense.orders)).first()
    response = client.post(
        url_for("expense.update_non_labor", expense_id=expense.id),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(
        url_for("expense.update_non_labor", expense_id=expense.id)
    )

    # database data
    assert db.session.query(Expense).count() == 4
    expense = NonLaborExpense.query.filter(not_(NonLaborExpense.orders)).first()
    assert expense.total == 150
    assert expense.supplier_id == 1
    assert expense.category == "operation:rent"

    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
def test_update_labor_get(client, user, expenses):
    expense = LaborExpense.query.filter(not_(LaborExpense.month.has())).first()
    response = client.get(
        url_for("expense.update", expense_id=expense.id), follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("expense.update_labor", expense_id=expense.id))
    assert "Update Labor Expense" in data

    for field in NonLaborExpenseForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField, BooleanField, FileField)):
            continue
        assert field.id in data
    assert "Update" in data

    assert url_for("expense.detail", expense_id=expense.id) in data


@pytest.mark.role("admin")
def test_update_labor_post_valid(client, user, expenses, image, today):
    expense = LaborExpense.query.filter(not_(LaborExpense.month.has())).first()
    request_data = {
        "date": today,
        "category": "labor:bonus",
        "employee": 1,
        "value-cash": 10,
        "value-card": 10,
        "value-check": 10,
        "value-transfer": 10,
    }
    response = client.post(
        url_for("expense.update_labor", expense_id=expense.id),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert url_for("expense.detail", expense_id=expense.id) in data

    # database data
    assert db.session.query(Expense).count() == 4
    expense = LaborExpense.query.filter(not_(LaborExpense.month.has())).first()
    assert expense.total == 40
    assert expense.date == today
    assert expense.employee_id == 1
    assert expense.category == "labor:bonus"

    # flash messege
    assert "Labor expense has been updated." in html.unescape(data)


@pytest.mark.role("admin")
def test_update_labor_post_invalid(client, user, expenses):
    expense = LaborExpense.query.filter(not_(LaborExpense.month.has())).first()
    response = client.post(
        url_for("expense.update_labor", expense_id=expense.id),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("expense.update_labor", expense_id=expense.id))

    # database data
    assert db.session.query(Expense).count() == 4
    expense = LaborExpense.query.filter(not_(LaborExpense.month.has())).first()
    assert expense.total == 150
    assert expense.employee_id == 1
    assert expense.category == "labor:advance"

    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
def test_update_order_payment_get(client, user, expenses):
    expense = NonLaborExpense.query.filter(NonLaborExpense.orders).first()
    response = client.get(
        url_for("expense.update", expense_id=expense.id), follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(
        url_for("expense.update_order_payment", expense_id=expense.id)
    )
    assert "Update Orders Payment" in data

    for field in NonLaborExpenseForm()._fields.values():
        if isinstance(field, (HiddenField, SubmitField, BooleanField, FileField)):
            continue
        assert field.id in data
    assert "Update" in data

    assert url_for("expense.detail", expense_id=expense.id) in data


@pytest.mark.role("admin")
def test_update_order_payment_post_valid(client, user, expenses, image, today):
    expense = NonLaborExpense.query.filter(NonLaborExpense.orders).first()
    request_data = {
        "date": today,
        "category": "operation:gas",
        "supplier": 1,
        "value-cash": 10,
        "value-card": 10,
        "value-check": 10,
        "value-transfer": 10,
        "orders": 1,
        "update": "Update",
    }
    response = client.post(
        url_for("expense.update_order_payment", expense_id=expense.id),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert url_for("expense.detail", expense_id=expense.id) in data

    # database data
    assert db.session.query(Expense).count() == 4
    expense = NonLaborExpense.query.filter(NonLaborExpense.orders).first()
    assert expense.total == 40
    assert expense.date == today
    assert expense.supplier_id == 1
    assert len(expense.orders) == 1
    assert expense.category == "operation:gas"

    # flash messege
    assert "Order Payment has been updated." in html.unescape(data)


@pytest.mark.role("admin")
def test_update_order_payment_post_invalid(client, user, expenses):
    expense = NonLaborExpense.query.filter(NonLaborExpense.orders).first()
    response = client.post(
        url_for("expense.update_order_payment", expense_id=expense.id),
        data={"update": "Update"},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(
        url_for("expense.update_order_payment", expense_id=expense.id)
    )

    # database data
    assert db.session.query(Expense).count() == 4
    expense = NonLaborExpense.query.filter(NonLaborExpense.orders).first()
    assert expense.total == 150
    assert expense.supplier_id == 1
    assert expense.category == "operation:rent"

    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
def test_update_salary_get(client, user, expenses):
    expense = LaborExpense.query.filter(LaborExpense.month.has()).first()
    response = client.get(
        url_for("expense.update", expense_id=expense.id), follow_redirects=True
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("expense.update_salary", expense_id=expense.id))
    assert "Update Salary" in data

    for field in NonLaborExpenseForm()._fields.values():
        if (
            isinstance(field, (HiddenField, SubmitField, BooleanField, FileField))
            or field.id == "category"
        ):
            continue
        assert field.id in data
    assert "Update" in data

    assert url_for("expense.detail", expense_id=expense.id) in data


@pytest.mark.role("admin")
def test_update_salary_post_valid(client, user, expenses, image, today):
    expense = LaborExpense.query.filter(LaborExpense.month.has()).first()
    request_data = {
        "date": today,
        "value-cash": 10,
        "value-card": 10,
        "value-check": 10,
        "value-transfer": 10,
    }
    response = client.post(
        url_for("expense.update_salary", expense_id=expense.id),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert url_for("expense.detail", expense_id=expense.id) in data

    # database data
    assert db.session.query(Expense).count() == 4
    expense = LaborExpense.query.filter(LaborExpense.month.has()).first()
    assert expense.total == 40
    assert expense.date == today
    assert expense.employee_id == 1

    # flash messege
    assert "Salary has been updated." in html.unescape(data)


@pytest.mark.role("admin")
def test_update_salary_post_invalid(client, user, expenses):
    expense = LaborExpense.query.filter(LaborExpense.month.has()).first()
    response = client.post(
        url_for("expense.update_salary", expense_id=expense.id),
        data={},
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200
    # url after request
    assert request.url.endswith(url_for("expense.update_salary", expense_id=expense.id))

    # database data
    assert db.session.query(Expense).count() == 4
    expense = LaborExpense.query.filter(LaborExpense.month.has()).first()
    assert expense.total == 150
    assert expense.employee_id == 1
    assert expense.category == "labor:salary"

    assert "This field is required." in html.unescape(data)
    assert "Total value must be greater than 0." in html.unescape(data)


@pytest.mark.role("admin")
def test_upload_post_valid(client, user, expenses, image):
    request_data = {
        "file": (image, "test.jpg"),
    }
    response = client.post(
        url_for("expense.upload", expense_id=1),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()
    assert response.status_code == 200
    assert request.url.endswith(url_for("expense.detail", expense_id=1))
    assert 'File "test.jpg" has been uploaded.' in html.unescape(data)
    assert db.session.query(ExpenseFile).count() == 1
    f = db.session.query(ExpenseFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.role("admin")
def test_upload_post_invalid_format(client, user, expenses):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.exe"),
    }
    response = client.post(
        url_for("expense.upload", expense_id=1),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("expense.detail", expense_id=1))
    assert 'Invalid file format ".exe".' in html.unescape(data)


@pytest.mark.role("admin")
def test_upload_post_invalid_empty(client, user, expenses):
    response = client.post(
        url_for("expense.upload", expense_id=1),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(url_for("expense.detail", expense_id=1))
    assert "No file has been uploaded." in html.unescape(data)


@pytest.mark.role("admin")
def test_salary_upload_post_valid(client, user, expenses, image, current_month):
    request_data = {
        "file": (image, "test.jpg"),
    }
    response = client.post(
        url_for("expense.salary_upload", month_str=current_month),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()
    assert response.status_code == 200
    assert request.url.endswith(
        url_for("expense.salary_index", month_str=current_month)
    )
    assert 'File "test.jpg" has been uploaded.' in html.unescape(data)
    assert db.session.query(SalaryPaymentFile).count() == 1
    f = db.session.query(SalaryPaymentFile).get(1)
    assert f.full_name == "test.jpg"
    assert os.path.isfile(f.path)


@pytest.mark.role("admin")
def test_salary_upload_post_invalid_format(client, user, expenses, current_month):
    request_data = {
        "file": (io.BytesIO(b"test"), "test.exe"),
    }
    response = client.post(
        url_for("expense.salary_upload", month_str=current_month),
        data=request_data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(
        url_for("expense.salary_index", month_str=current_month)
    )
    assert 'Invalid file format ".exe".' in html.unescape(data)


@pytest.mark.role("admin")
def test_salary_upload_post_invalid_empty(client, user, expenses, current_month):
    response = client.post(
        url_for("expense.salary_upload", month_str=current_month),
        data={},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(
        url_for("expense.salary_index", month_str=current_month)
    )
    assert "No file has been uploaded." in html.unescape(data)


@pytest.mark.role("admin")
def test_delete_post(client, user, expenses):
    response = client.post(
        url_for("expense.delete", expense_id=1),
        follow_redirects=True,
    )
    data = response.data.decode()

    assert response.status_code == 200
    assert request.url.endswith(
        url_for("expense.index", date_str=datetime.date.today())
    )
    assert "Expense has been deleted." in html.unescape(data)

    assert Expense.query.count() == 3
    assert not Expense.query.get(1)
