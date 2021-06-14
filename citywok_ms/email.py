from flask.templating import render_template
from flask_mail import Message

from citywok_ms import mail


def send_invite_email(invitee, token):
    send_email(
        "[CityWok-Manager] Invite",
        recipients=[invitee],
        text_body=render_template("email/invite.txt", token=token),
        html_body=render_template("email/invite.html", token=token),
    )


def send_confirmation_email(target, token, username):
    send_email(
        "[CityWok-Manager] Confirmation",
        recipients=[target],
        text_body=render_template(
            "email/confirmation.txt", token=token, username=username
        ),
        html_body=render_template(
            "email/confirmation.html", token=token, username=username
        ),
    )


def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
