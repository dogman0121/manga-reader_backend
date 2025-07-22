from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.jwt import jwt
from flask_cors import CORS
from app.storage import Storage

migrate = Migrate()
db = SQLAlchemy()
mail = Mail()
cors = CORS()
storage = Storage()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    storage.init_app(app)

    from app.user import bp as user_bp
    app.register_blueprint(user_bp)

    from app.search import bp as search_bp
    app.register_blueprint(search_bp)

    from app.manga import bp as manga_bp
    app.register_blueprint(manga_bp)

    from app.comments import bp as comment_bp
    app.register_blueprint(comment_bp)

    from app.chapters import bp as chapters_bp
    app.register_blueprint(chapters_bp, url_prefix='/api/v1/chapters')

    from app.teams import bp as teams_bp
    app.register_blueprint(teams_bp, url_prefix='/api/v1/teams')

    from app.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp, url_prefix='/api/v1/notifications')

    from app.lists import bp as lists_bp
    app.register_blueprint(lists_bp, url_prefix='/api/v1/lists')

    from app.home import bp as home_bp
    app.register_blueprint(home_bp, url_prefix='/api/v1/home')

    from app.admin import admin
    admin.init_app(app)

    return app