from manage import *
from app.user.models import User
from app.manga.models import Type, Genre, Status, Adult


from app import db

with app.app_context():
    db.create_all()

    db.session.add(User("a", "vasilevib@yandex.ru", "12345678"))
    db.session.add(User("b", "giachetti101@gmail.com", "12345678"))

    db.session.add(Type(name="нет"))

    db.session.add(Status(name="нет"))

    db.session.add(Adult(name="нет"))

    db.session.add(Genre(name="драки"))

    db.session.commit()