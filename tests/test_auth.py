import html

import pytest
from citywok_ms import db
from citywok_ms.auth.models import User
from flask import request, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def test_login_get(client):
    response = client.get(
        url_for("auth.login"),
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("auth.login"))

    # titles
    assert "Login" in data
    assert "CityWok Manager" in data
    assert "User Name" in data
    assert "Password" in data
    assert "Login" in data

    # links
    assert url_for("auth.forget_password") in data


@pytest.mark.role("admin")
def test_login_get_loggedin(client, user):
    response = client.get(
        url_for("auth.login"),
        follow_redirects=True,
    )

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("main.index"))


def test_login_post_valid(client, user):
    request_data = {
        "username": "user",
        "password": "user",
    }
    response = client.post(
        url_for("auth.login"),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("main.index"))

    assert f"Welcome {user.username}, you are logged in." in html.unescape(data)


def test_login_post_invalid(client, user):
    request_data = {
        "username": "wrong",
        "password": "wrong",
    }
    response = client.post(
        url_for("auth.login"),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("auth.login"))

    assert "Please check your username/password." in html.unescape(data)


def test_logout_get(client):
    response = client.get(
        url_for("auth.logout"),
        follow_redirects=True,
    )

    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("auth.login"))
    assert "You have been logged out." in html.unescape(data)


def test_logout_post(client):
    response = client.post(
        url_for("auth.logout"),
        follow_redirects=True,
    )

    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("auth.login"))
    assert "You have been logged out." in html.unescape(data)


@pytest.mark.role("admin")
def test_invite_get(client, user):
    response = client.get(
        url_for("auth.invite"),
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert request.url.endswith(url_for("auth.invite"))

    # titles
    assert "Invite" in data
    assert "Invitee's E-mail" in html.unescape(data)
    assert "Role" in data
    assert "Invite" in data

    # links
    assert url_for("main.index") in data


@pytest.mark.role("admin")
def test_invite_post_valid(client, user):
    request_data = {
        "email": "test@mail.com",
        "role": "manager",
    }
    response = client.post(
        url_for("auth.invite"),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert url_for("auth.invite") in request.url

    assert "A invite e-mail has been sent to the envitee." in data

    # links
    assert url_for("main.index") in data


@pytest.mark.role("admin")
def test_invite_post_invalid_email(client, user):
    response = client.post(
        url_for("auth.invite"),
        data={
            "email": "user@mail.com",
            "role": "manager",
        },
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert url_for("auth.invite") in request.url

    # titles
    assert "Invite link" not in data
    assert "A invite e-mail has been sent to the envitee." not in data

    assert "E-mail address already taken." in data


def test_registration_get(client):
    response = client.get(
        url_for(
            "auth.registration",
            token=User.create_invite_token("manager", "test@mail.com"),
        )
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Register" in data
    assert "User Name" in data
    assert "Password" in data
    assert "Repeat Password" in data
    assert "Regist" in data

    # links
    assert url_for("auth.login") in data


@pytest.mark.role("admin")
def test_registration_get_loggedin(client, user):
    response = client.get(
        url_for(
            "auth.registration",
            token=User.create_invite_token("manager", "test@mail.com"),
        ),
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "You are already logged in." in data

    assert request.url.endswith(url_for("main.index"))


def test_registration_get_invalid_token(client):
    response = client.post(
        url_for(
            "auth.registration",
            token="xxx",
        ),
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Invite link is invalid." in data

    assert request.url.endswith(url_for("auth.login"))


def test_registration_post_valid(client):
    request_data = {
        "username": "test_user",
        "password": "password",
        "password2": "password",
    }
    response = client.post(
        url_for(
            "auth.registration",
            token=User.create_invite_token("manager", "test@mail.com"),
        ),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "You are now registed." in data

    assert request.url.endswith(url_for("auth.login"))

    assert (
        db.session.query(User)
        .filter_by(email="test@mail.com", username="test_user")
        .count()
        == 1
    )


def test_registration_post_invalid_existed(client):
    user = User(
        username="test",
        email="test@mail.com",
        password=generate_password_hash("test"),
        role="manager",
    )
    db.session.add(user)
    db.session.commit()
    request_data = {
        "username": "test",
        "password": "password",
        "password2": "password",
    }
    response = client.post(
        url_for(
            "auth.registration",
            token=User.create_invite_token("manager", "test@mail.com"),
        ),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "You are now registed." not in data
    assert "This email has already been registed." in data

    assert db.session.query(User).filter_by(email="test@mail.com").count() == 1
    assert request.url.endswith(url_for("auth.login"))


def test_registration_post_invalid_username(client):
    user = User(
        username="test",
        email="test@mail.com",
        password=generate_password_hash("test"),
        role="manager",
    )
    db.session.add(user)
    db.session.commit()
    request_data = {
        "username": "test",
        "password": "password",
        "password2": "password",
    }
    response = client.post(
        url_for(
            "auth.registration",
            token=User.create_invite_token("manager", "test2@mail.com"),
        ),
        data=request_data,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "You are now registed." not in data
    assert "Please use a different username." in data

    assert db.session.query(User).filter_by(email="test2@mail.com").count() == 0


def test_forget_password_get(client):
    response = client.get(url_for("auth.forget_password"))
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Forget Password" in data
    assert "Email" in data
    assert "Submit" in data

    # links
    assert url_for("auth.login") in data


def test_forget_password_post_valid(client):
    user = User(
        username="test",
        email="test@mail.com",
        password=generate_password_hash("test"),
        role="manager",
    )
    db.session.add(user)
    db.session.commit()

    request_data = {"email": "test@mail.com"}
    response = client.post(
        url_for("auth.forget_password"),
        data=request_data,
        follow_redirects=True,
    )

    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert f"A e-mail to reset the password has been sent to {user.email}." in data


def test_forget_password_post_invalid_email(client):
    user = User(
        username="test",
        email="test@mail.com",
        password=generate_password_hash("test"),
        role="manager",
    )
    db.session.add(user)
    db.session.commit()

    request_data = {"email": "test2@mail.com"}
    response = client.post(
        url_for("auth.forget_password"),
        data=request_data,
    )

    data = response.data.decode()

    # state code
    assert response.status_code == 200

    assert "A e-mail to reset the password has been sent to test2@mail.com." not in data
    assert "User with this e-mail address do not exist." in data


def test_reset_password_get(client):
    user = User(
        username="test",
        email="test@mail.com",
        password=generate_password_hash("test"),
        role="manager",
    )
    db.session.add(user)
    db.session.commit()

    response = client.get(
        url_for(
            "auth.reset_password",
            token=user.create_reset_token(),
        ),
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Reset Password" in data

    assert "Password" in data
    assert "Repeat Password" in data

    assert url_for("auth.login") in data


def test_reset_password_get_invalid_token(client):
    user = User(
        username="test",
        email="test@mail.com",
        password=generate_password_hash("test"),
        role="manager",
    )
    db.session.add(user)
    db.session.commit()
    response = client.get(
        url_for(
            "auth.reset_password",
            token="xxx",
        ),
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Reset link is invalid." in data

    assert request.url.endswith(url_for("auth.login"))


def test_reset_password_post_valid(client):
    user = User(
        username="test",
        email="test@mail.com",
        password=generate_password_hash("test"),
        role="manager",
    )
    db.session.add(user)
    db.session.commit()
    request_data = {
        "password": "new",
        "password2": "new",
    }
    response = client.post(
        url_for(
            "auth.reset_password",
            token=user.create_reset_token(),
        ),
        data=request_data,
        follow_redirects=True,
    )
    data = response.data.decode()

    # state code
    assert response.status_code == 200

    # titles
    assert "Your password has been reset." in data

    assert request.url.endswith(url_for("auth.login"))

    assert check_password_hash(user.password, "new")
