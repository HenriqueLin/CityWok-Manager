from citywok_ms import db, login
from citywok_ms.utils.models import CRUDMixin
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import ChoiceType
from werkzeug.security import check_password_hash, generate_password_hash
from flask_babel import lazy_gettext as _l

Role = [
    ("admin", _l("Admin")),
    ("manager", _l("Manager")),
    ("shareholder", _l("Shareholder")),
    ("worker", _l("Worker")),
    ("visitor", _l("Visitor")),
]


@login.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


class User(db.Model, UserMixin, CRUDMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(ChoiceType(Role), nullable=False)

    def __repr__(self):
        return f"User({self.id}: {self.username}, {self.email}, {self.role.code})"

    @classmethod
    def create_by_form(cls, form, role: str) -> "User":
        user = cls()
        form.populate_obj(user)
        user.set_password(form.password.data)
        user.role = role
        db.session.add(user)
        return user

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    @classmethod
    def authenticate_user(cls, username: str, password: str) -> "User":
        user = cls.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return user

    @staticmethod
    def create_invite_token(role, email, expires_sec=86400):  # 1 day
        s = TimedSerializer(current_app.secret_key, expires_sec)
        return s.dumps({"role": role, "email": email}).decode("utf-8")

    @staticmethod
    def verify_invite_token(token):
        s = TimedSerializer(current_app.secret_key)
        try:
            role = s.loads(token)["role"]
            email = s.loads(token)["email"]
        except Exception:
            return
        return role, email

    def create_reset_token(self, expires_sec=7200):  # 2 hour
        s = TimedSerializer(current_app.secret_key, expires_sec)
        return s.dumps({"id": self.id, "email": self.email}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = TimedSerializer(current_app.secret_key)
        try:
            id = s.loads(token)["id"]
            email = s.loads(token)["email"]
        except Exception:
            return
        user = db.session.query(User).filter_by(id=id, email=email).first()
        return user

    @classmethod
    def get_by_email(cls, email) -> "User":
        return db.session.query(User).filter_by(email=email).first()
