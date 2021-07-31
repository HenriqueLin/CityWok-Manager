import html
from flask import url_for, request


def test_401(client):
    response = client.get(url_for("error._401"), follow_redirects=True)
    data = response.data.decode()

    assert response.status_code == 200

    assert "Please log in to access this page." in data
    assert request.url.endswith(url_for("auth.login"))


def test_403(client):
    response = client.get(url_for("error._403"))
    data = response.data.decode()

    assert response.status_code == 403

    assert (
        "Ops, seems like you don't have the permission to visit this page."
        in html.unescape(data)
    )
    assert "403" in data
    assert url_for("main.index") in data


def test_404(client):
    response = client.get(url_for("error._404"))
    data = response.data.decode()

    assert response.status_code == 404

    assert "File Not Found." in data
    assert "Please check if the url is correct." in data
    assert "404" in data
    assert url_for("main.index") in data


def test_500(client):
    response = client.get(url_for("error._500"))
    data = response.data.decode()

    assert response.status_code == 500

    assert "An unexpected error has occurred" in data
    assert "The administrator has been notified." in data
    assert "500" in data
    assert url_for("main.index") in data
