from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret')
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default_flask_secret')

class DevelopmentConfig(Config):
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': Config,
    'default': Config
}