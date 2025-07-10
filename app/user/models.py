from flask import current_app

from app import db, storage
from app.models import Base
from app.notifications import NotificationService
from app.notifications.models import Notification

from sqlalchemy import Table, ForeignKey, Column, String, Integer, DateTime, Text, insert, delete, select, and_, func, Select
from sqlalchemy.orm import mapped_column, Mapped, relationship

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

user_subscribers = Table(
    'user_subscriber',
    db.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False, primary_key=True),
    Column("subscriber_id", Integer, ForeignKey("user.id"), nullable=False, primary_key=True),
)

class Avatar(Base):
    __tablename__ = "avatar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(64), nullable=False)

class UserService:
    def __init__(self):
        pass

    @staticmethod
    def get_user(user_id=None, login=None, email=None):
        if user_id:
            return User.query.get(user_id)
        if login:
            return User.query.filter_by(login=login).first()
        if email:
            return User.query.filter_by(email=email).first()


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    about: Mapped[str] = mapped_column(Text, nullable=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password: Mapped[str] = db.Column(Text, nullable=False)
    role: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    avatar: Mapped["Avatar"] = relationship(Avatar)
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", uselist=True, foreign_keys="Notification.user_id")
    lists: Mapped[list["List"]] = relationship(back_populates="creator", foreign_keys="List.creator_id", uselist=True)

    def __init__(self, login, email, password):
        self.set_login(login)
        self.set_email(email)
        self.set_password(password)

    @staticmethod
    def get_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_login(login):
        return User.query.filter_by(login=login).scalar()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).scalar()

    @staticmethod
    def search(query):
        return db.session.execute(
            Select(User).filter(func.lower(User.login).like(f"%{query.lower()}%"))
        ).scalars().all()

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

    ###### Subscribe ######

    def subscribe(self, subscriber):
        try:
            db.session.execute(insert(user_subscribers).values(user_id=self.id, subscriber_id=subscriber.id))
            db.session.commit()
        except Exception:
            pass

    def unsubscribe(self, subscriber):
        try:
            db.session.execute(delete(user_subscribers)
                               .where(and_(user_subscribers.c.user_id == self.id,
                                           user_subscribers.c.subscriber_id == subscriber.id
                                           )))
            db.session.commit()
        except Exception:
            pass

    def is_subscribed(self, subscriber):
        return db.session.execute(select(user_subscribers)
            .where(and_(
                user_subscribers.c.user_id == self.id,
                user_subscribers.c.subscriber_id == subscriber.id
        ))).scalar() is not None

    def get_subscribers(self, page=1, per_page=20):
        return db.session.execute(Select(User)
            .join(user_subscribers, onclause=User.id == user_subscribers.c.subscriber_id)
            .where(self.id == user_subscribers.c.user_id)
            .offset((page-1) * per_page).limit(per_page)
        ).scalars()

    def get_subscribers_count(self):
        return db.session.execute(select(func.count(user_subscribers.c.user_id))
            .where(self.id == user_subscribers.c.user_id)
        ).scalar()

    def get_subscribed(self, page=1, per_page=20):
        return db.session.execute(Select(User)
            .join(user_subscribers, onclause=User.id == user_subscribers.c.user_id)
            .where(self.id == user_subscribers.c.subscriber_id)
            .offset((page-1) * per_page).limit(per_page)
        )

    def get_subscriber_count(self):
        return db.session.execute(select(func.count(user_subscribers.c.user_id))
            .where(self.id == user_subscribers.c.subscriber_id)
        )
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
            return User.query.get(user_id, )
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

    def to_dict(self, user=None, with_lists=False):
        data = {
            "id": self.id,
            "login": self.login,
            "email": self.email,
            "role": self.role,
            "created_at": datetime.strftime(self.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "subscribed": None if user is None else self.is_subscribed(user),
            "avatar": storage.get_url(f"user/{self.id}/{self.avatar.filename}") if self.avatar else None,
            "about": self.about,
            "subscribers_count": self.get_subscribers_count(),
            "notifications_count": NotificationService.get_unread_user_notifications_count(self),
        }

        if with_lists:
            data["lists"] = [l.to_dict() for l in self.lists]

        return data
