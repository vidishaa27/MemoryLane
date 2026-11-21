import os
from dotenv import load_dotenv

# Load environment variables from .env file at repo root or backend dir
basedir = os.path.abspath(os.path.dirname(__file__))
rootdir = os.path.abspath(os.path.join(basedir, ".."))

# Check for .env in root or backend
if os.path.exists(os.path.join(rootdir, ".env")):
    load_dotenv(os.path.join(rootdir, ".env"))
elif os.path.exists(os.path.join(basedir, ".env")):
    load_dotenv(os.path.join(basedir, ".env"))
else:
    load_dotenv()

DEFAULT_DB_PATH = os.path.join(basedir, "database.db")

class Config:
    APP_ENV = os.getenv("APP_ENV", "development").lower()

    # Secret key configuration
    SECRET_KEY = os.getenv("SECRET_KEY")
    if APP_ENV == "production" and not SECRET_KEY:
        raise RuntimeError(
            "CRITICAL SECURITY ERROR: 'SECRET_KEY' environment variable is missing in production. "
            "Please configure a secure SECRET_KEY in your environment or .env file."
        )
    elif not SECRET_KEY:
        # Fallback for development/testing if not set in .env
        SECRET_KEY = "dev-secret-key-replace-in-production"

    # Database URL configuration
    # Note: Flask-SQLAlchemy 3 resolves relative SQLite URLs against instance/.
    # If DATABASE_URL is not provided, fall back to the absolute path of backend/database.db.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{DEFAULT_DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookie security configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (APP_ENV == "production")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
