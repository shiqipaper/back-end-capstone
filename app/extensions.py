from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

@jwt.invalid_token_loader
def invalid_token_loader(reason):
    return jsonify({"message": reason}), 401

@jwt.expired_token_loader
def expired_token_loader(header, payload):
    return jsonify({"message": "Token has expired"}), 401