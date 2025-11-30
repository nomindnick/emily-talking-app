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

    # Load configuration (instantiate to trigger __init__ for production validation)
    config_class = config[config_name]
    app.config.from_object(config_class())

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Login
    from app.auth import login_manager

    login_manager.init_app(app)

    # Register routes
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    # Auto-initialize database (idempotent - safe for Railway restarts)
    # Skip in testing mode - tests manage their own database state
    if not app.config.get("TESTING"):
        with app.app_context():
            db.create_all()
            # Seed users and categories if they don't exist
            from app.init_db import seed_categories, seed_users

            seed_users()
            seed_categories()

    return app
