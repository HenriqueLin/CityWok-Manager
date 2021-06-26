from flask import has_request_context, request
from flask_login import current_user as user
import logging


class MyFormatter(logging.Formatter):  # test: no cover
    def __init__(self, fmt, style) -> None:
        super().__init__(fmt=fmt, style=style)

    def format(self, record):
        if user:
            if user.is_authenticated:
                record.user = str(user)
            else:
                record.user = "anonymous"
        else:
            record.user = "-"
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
        else:
            record.url = "-"
            record.method = "-"
            record.remote_addr = "-"

        return super().format(record)


formatter = MyFormatter(
    "[{levelname} - {asctime}] {user} {remote_addr} at {pathname}:{lineno}\n"
    "  {message}",
    style="{",
)
