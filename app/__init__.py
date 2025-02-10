from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate, bcrypt, jwt
from app.routes.plant_routes import plants_bp
from app.routes.user_routes import users_bp
from config import Config


def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(Config)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is not set. Please check your environment variables.")
    if not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError("JWT_SECRET_KEY is not set. Please check your environment variables.")
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is not set. Please check your environment variables.")

    if config:
        app.config.update(config)

    app.url_map.strict_slashes = False

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(plants_bp, url_prefix="/plants")
    app.register_blueprint(users_bp, url_prefix="/users")

    return app
