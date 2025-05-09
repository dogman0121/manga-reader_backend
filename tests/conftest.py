import pytest
from flask_jwt_extended import create_access_token
from app import create_app, db
from config import Config

@pytest.fixture()
def app():
    app = create_app(Config)
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here
    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()
    # clean up / reset resources here


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture()
def jwt_token():
    return create_access_token(identity=1)

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()