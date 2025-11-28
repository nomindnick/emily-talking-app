"""Application configuration classes."""

import os


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Baby birthdate for milestone calculations
    BABY_BIRTHDATE = os.environ.get("BABY_BIRTHDATE")

    # User display names
    WIFE_DISPLAY_NAME = os.environ.get("WIFE_DISPLAY_NAME", "Partner")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///dev.db"
    )


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """Get database URI, handling Railway's postgres:// format."""
        uri = os.environ.get("DATABASE_URL")
        if uri and uri.startswith("postgres://"):
            # Railway uses postgres:// but SQLAlchemy requires postgresql://
            uri = uri.replace("postgres://", "postgresql://", 1)
        return uri


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
