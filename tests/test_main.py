from flask import url_for


def test_index_get(client, admin):
    response = client.get(url_for("main.index"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert "CityWok-Manager" in data
    assert "Home" in data


def test_index_post(client):
    response = client.post(url_for("main.index"))

    # state code
    assert response.status_code == 405
