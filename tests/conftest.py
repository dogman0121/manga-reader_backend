import pytest
from config import TestConfig
from app import create_app, db


@pytest.fixture()
def app():
    app = create_app(TestConfig)

    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.rollback()
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()