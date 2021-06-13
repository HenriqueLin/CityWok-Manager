from flask_login import UserMixin
from citywok_ms import db, login
from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import ChoiceType
from werkzeug.security import check_password_hash


Role = [
    ("admin", "Admin"),
    ("manager", "Manager"),
    ("woker", "Woker"),
    ("visiter", "Visiter"),
]


@login.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(ChoiceType(Role), nullable=False)

    def __repr__(self):
        return f"User('{self.role}','{self.username}','{self.email}')"

    @classmethod
    def authenticate_user(cls, username: str, password: str) -> "User":
        user = cls.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return user
