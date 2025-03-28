from manage import app
from app import db
from sqlalchemy import text

with app.app_context():
    # db.drop_all()
    # db.session.execute(text("DROP TABLE manga CASCADE"))
    db.session.execute(text("delete from alembic_version;"))
    db.session.commit()