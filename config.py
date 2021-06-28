import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    # general
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    LANGUAGES = ["en", "zh"]
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(basedir, "uploads")

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # admin
    ADMIN_NAME = os.environ.get("ADMIN_NAME")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

    # mail
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("ADMIN_EMAIL")

    # sentry
    SENTRY_DNS = os.environ.get("SENTRY_DNS")
    SENTRY_RATE = os.environ.get("SENTRY_RATE")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MAIL_SUPPRESS_SEND = True
    ADMIN_NAME = "admin"
    ADMIN_EMAIL = "admin@mail.com"
    ADMIN_PASSWORD = "admin_password"
    RQ_CONNECTION_CLASS = "fakeredis.FakeStrictRedis"
    RQ_ASYNC = False
