import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    # general
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    LANGUAGES = ["en"]
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(basedir, "uploads")

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # admin
    ADMIN_NAME = os.environ.get("ADMIN_NAME") or "Admin"
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL") or None
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "admin"

    # mail
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
