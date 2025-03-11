from manage import app
from app import db
from sqlalchemy import text

with app.app_context():
    db.session.execute(text("drop schema public cascade; create schema public;"))
    db.session.commit()