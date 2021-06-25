from flask import url_for
import pytest


@pytest.mark.role("admin")
def test_get(client, user):
    response = client.get(url_for("admin.index"))

    # state code
    assert response.status_code == 200
