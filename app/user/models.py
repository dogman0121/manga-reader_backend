from flask import current_app
from app import db
from sqlalchemy import Table, ForeignKey, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time

oauth = Table(
    'oauth',
    db.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("oauth_type", String(20), nullable=False),
    Column("oauth_id", Text, nullable=False),
)

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password: Mapped[str] = db.Column(Text, nullable=False)
    role: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


    @staticmethod
    def get_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_login(login):
        return User.query.filter_by(login=login).scalar()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).scalar()

    def __init__(self, login, email, password):
        self.set_login(login)
        self.set_email(email)
        self.set_password(password)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    ###### Setting credentials ######

    @staticmethod
    def validate_login(login):
        return len(login) <= 64

    @staticmethod
    def validate_email(email):
        return len(email) <= 320

    @staticmethod
    def validate_password(password):
        return len(password) >= 8

    def set_login(self, login):
        if User.validate_login(login):
            self.login = login
        else:
            raise Exception('login must be shorter than 64 characters')

    def set_email(self, email):
        if User.validate_email(email):
            self.email = email
        else:
            raise Exception('email must be shorter than 320 characters')

    def set_password(self, password):
        self.password = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password, password)

    ################################

    ###### Getting and verifying tokens ######

    def get_recovery_token(self):
        return jwt.encode({
            'id': self.id,
            'exp': time() + 600
        }, current_app.config["SECRET_KEY"], algorithm='HS256')

    @staticmethod
    def verify_recovery_token(token):
        try:
            user_id = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])["id"]
            return User.query.get(user_id)
        except Exception:
            return None

    @staticmethod
    def get_registration_token(login, email, password):
        return jwt.encode({
            'login': login,
            'email': email,
            'password': password,
            'exp': time() + 600
        }, current_app.config["SECRET_KEY"], algorithm='HS256')

    @staticmethod
    def verify_registration_token(token):
        try:
            return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=['HS256'])
        except Exception:
            return

    ################################

    def to_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "email": self.email,
            "role": self.role,
            "created_at": datetime.strftime(self.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        }
