import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///default.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
