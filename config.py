import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ["en"]
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(basedir, "uploads")

    ADMIN_NAME = os.environ.get("ADMIN_NAME") or "Admin"
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL") or None
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "admin"


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
