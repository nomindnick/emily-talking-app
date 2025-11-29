"""Pytest configuration and fixtures."""

import pytest

from app import create_app, db
from app.models import User


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
