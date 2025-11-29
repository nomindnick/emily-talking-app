"""Authentication module for Flask-Login configuration."""

from flask_login import LoginManager

from app.models import User

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Please log in to access this page."


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login session management."""
    return User.query.get(int(user_id))
