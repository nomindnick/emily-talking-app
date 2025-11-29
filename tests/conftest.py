"""Pytest configuration and fixtures."""

import pytest

from app import create_app, db


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
