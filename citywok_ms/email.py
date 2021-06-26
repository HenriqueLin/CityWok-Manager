from threading import Thread
from flask.templating import render_template
from flask_mail import Message
from flask import current_app
from citywok_ms import mail


def send_password_reset_email(user, token):
    send_email(
        "[CityWok-Manager] Reset Password",
        recipients=[user.email],
        text_body=render_template(
            "email/password_reset.txt", token=token, username=user.username
        ),
        html_body=render_template(
            "email/password_reset.html", token=token, username=user.username
        ),
    )


def send_invite_email(invitee, token):
    send_email(
        "[CityWok-Manager] Invite",
        recipients=[invitee],
        text_body=render_template("email/invite.txt", token=token),
        html_body=render_template("email/invite.html", token=token),
    )


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg),
    ).start()
