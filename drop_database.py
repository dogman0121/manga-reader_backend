from manage import app
from app import db
from sqlalchemy import text

with app.app_context():
    db.drop_all()
    db.session.commit()