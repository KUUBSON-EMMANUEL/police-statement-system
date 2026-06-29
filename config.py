"""
Configuration settings for the Police Statement Management System.

Different configuration profiles are provided for development and
production. In production, set environment variables (SECRET_KEY,
DATABASE_URL) rather than relying on the defaults below.
"""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core security settings -------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this-in-production")

    # --- Database -----------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Session / auth -------------------------------------------------------
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # auto session timeout
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # In production behind HTTPS, also set SESSION_COOKIE_SECURE = True

    # --- File uploads ---------------------------------------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "doc", "docx", "gif"}

    # --- CSRF -------------------------------------------------------------------
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # tied to session lifetime instead

    # --- Pagination -------------------------------------------------------------
    STATEMENTS_PER_PAGE = 15


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    )


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    # Example for Postgres: postgresql://user:password@host:5432/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
