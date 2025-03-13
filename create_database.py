from manage import *
from app.user.models import User

from app import db

with app.app_context():
    db.create_all()

    user = User("a", "vasilevib@yandex.ru", "12345678")
    user.add()