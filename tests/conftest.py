"""Pytest configuration and fixtures."""

from datetime import datetime, timedelta, timezone

import pytest

from app import create_app, db
from app.models import Category, User, Word


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Provide a database session for testing.

    This fixture ensures tests run within a transaction that gets
    rolled back after each test for isolation.
    """
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def seeded_db(app):
    """Create database with seeded test users.

    Creates two users with known password 'testpass' for authentication tests.
    """
    with app.app_context():
        # Create test users
        nick = User(username="nick", display_name="Nick")
        nick.set_password("testpass")
        db.session.add(nick)

        wife = User(username="wife", display_name="Partner")
        wife.set_password("testpass")
        db.session.add(wife)

        db.session.commit()
        yield db
        db.session.rollback()


@pytest.fixture
def authenticated_client(app, seeded_db):
    """Create a test client with an authenticated user session."""
    client = app.test_client()

    with client:
        # Log in as nick
        client.post("/login", data={
            "username": "nick",
            "password": "testpass"
        }, follow_redirects=True)
        yield client


@pytest.fixture
def sample_words(authenticated_client, seeded_db):
    """Create sample words for testing word list functionality.

    Creates words with different dates, users, and categories for testing
    sorting and filtering. Uses authenticated_client to ensure proper context.
    """
    # Get the users
    nick = User.query.filter_by(username="nick").first()
    wife = User.query.filter_by(username="wife").first()

    # Create categories
    noun = Category(name="Noun", description="Things")
    verb = Category(name="Verb", description="Actions")
    db.session.add(noun)
    db.session.add(verb)
    db.session.commit()

    # Create words with different dates, users, and categories
    now = datetime.now(timezone.utc)
    words_data = [
        {"word": "apple", "user": nick, "category": noun, "days_ago": 10},
        {"word": "banana", "user": wife, "category": noun, "days_ago": 5},
        {"word": "cat", "user": nick, "category": None, "days_ago": 3},
        {"word": "dog", "user": wife, "category": noun, "days_ago": 1},
        {"word": "eat", "user": nick, "category": verb, "days_ago": 7},
    ]

    words = []
    for data in words_data:
        word = Word(
            word=data["word"],
            user_id=data["user"].id,
            category_id=data["category"].id if data["category"] else None,
            date_added=now - timedelta(days=data["days_ago"]),
        )
        db.session.add(word)
        words.append(word)

    db.session.commit()

    # Refresh to load relationships
    for word in words:
        db.session.refresh(word)

    return words
