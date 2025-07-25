from flask_sqlalchemy import SQLAlchemy

sqlalchemy_db = SQLAlchemy()

class SQLAlchemyAdapter:

    def __init__(self, app):
        if app.config["SQLALCHEMY_DATABASE_URI"] is not None:
            sqlalchemy_db.init_app(app)


def setup_sqlalchemy(app):
    SQLAlchemyAdapter(app)

    return app