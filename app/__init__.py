from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

migrate = Migrate()
db = SQLAlchemy()
mail = Mail()
jwt = JWTManager()
cors = CORS()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')

    from app.person import bp as person_bp
    app.register_blueprint(person_bp, url_prefix='/api/person')

    return app