"""Flask application factory."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()


def create_app(config_name="default"):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration to use (development, production, testing, default)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Register routes
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app
