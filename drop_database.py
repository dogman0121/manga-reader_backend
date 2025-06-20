from manage import app
from app import db
from sqlalchemy import text

with app.app_context():
    #db.drop_all()
    db.session.execute(text("DELETE FROM manga_poster"))
    # db.session.execute(text("delete from alembic_version;"))
    db.session.commit()