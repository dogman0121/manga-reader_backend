from app import db
from sqlalchemy import Table, ForeignKey
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


oauth = Table(
    'oauth',
    db.metadata,
    db.Column("user_id", db.Integer, ForeignKey("user.id"), nullable=False),
    db.Column("oauth_type", db.String(20), nullable=False),
    db.Column("oauth_id", db.String(150), nullable=False),
)

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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
        self.login = login
        self.email = email
        self.password = generate_password_hash(password)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "email": self.email,
            "role": self.role,
            "created_at": datetime.strftime(self.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        }
