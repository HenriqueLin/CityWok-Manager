import os


class Config():
    SECRET_KEY = 'b49c18b38c3f124f8f190534ef7a2833'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
