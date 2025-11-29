"""Database initialization script.

Creates all tables and seeds initial data (users and categories).
"""

import os

from app import create_app, db
from app.models import Category, User


def init_db():
    """Initialize the database with tables and seed data."""
    app = create_app(os.environ.get("FLASK_ENV", "development"))

    with app.app_context():
        # Create all tables
        db.create_all()

        # Seed users if they don't exist
        seed_users()

        # Seed categories if they don't exist
        seed_categories()

        print("Database initialized successfully!")


def seed_users():
    """Seed the two parent user accounts."""
    # Check if users already exist
    if User.query.filter_by(username="nick").first():
        print("Users already exist, skipping user seeding.")
        return

    # Get passwords from environment variables
    nick_password = os.environ.get("NICK_PASSWORD", "devpassword")
    wife_password = os.environ.get("WIFE_PASSWORD", "devpassword")
    wife_display_name = os.environ.get("WIFE_DISPLAY_NAME", "Wife")

    # Create Nick's account
    nick = User(username="nick", display_name="Nick")
    nick.set_password(nick_password)
    db.session.add(nick)

    # Create wife's account
    wife = User(username="wife", display_name=wife_display_name)
    wife.set_password(wife_password)
    db.session.add(wife)

    db.session.commit()
    print(f"Created users: Nick, {wife_display_name}")


def seed_categories():
    """Seed default word categories."""
    # Check if categories already exist
    if Category.query.first():
        print("Categories already exist, skipping category seeding.")
        return

    default_categories = [
        ("Noun", "People, places, things"),
        ("Verb", "Action words"),
        ("Animal Sound", "Sounds animals make (moo, woof, etc.)"),
        ("Person", "Names of people (mama, dada, etc.)"),
        ("Other", "Words that don't fit other categories"),
    ]

    for name, description in default_categories:
        category = Category(name=name, description=description)
        db.session.add(category)

    db.session.commit()
    print(f"Created {len(default_categories)} categories")


if __name__ == "__main__":
    init_db()
