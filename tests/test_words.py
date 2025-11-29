"""Tests for word entry functionality (Sprint 3)."""

import pytest

from app.models import Word


def test_add_word_success(authenticated_client, seeded_db):
    """Can add a new word."""
    response = authenticated_client.post("/words/add", data={
        "word": "hello"
    }, follow_redirects=True)

    assert response.status_code == 200

    # Verify word in database
    word = Word.query.filter_by(word="hello").first()
    assert word is not None
    assert word.user_id is not None
    assert word.date_added is not None


def test_add_word_duplicate_rejected(authenticated_client, seeded_db):
    """Duplicate words are rejected."""
    # Add first word
    authenticated_client.post("/words/add", data={"word": "hello"})

    # Try to add duplicate
    response = authenticated_client.post("/words/add", data={
        "word": "hello"
    }, follow_redirects=True)

    # Should show error, not add second word
    assert Word.query.filter_by(word="hello").count() == 1
    assert b"already been added" in response.data


def test_duplicate_check_case_insensitive(authenticated_client, seeded_db):
    """Duplicate check ignores case."""
    authenticated_client.post("/words/add", data={"word": "Hello"})

    response = authenticated_client.post("/words/add", data={
        "word": "HELLO"
    }, follow_redirects=True)

    # Should reject as duplicate
    assert Word.query.count() == 1


def test_word_tracks_user(authenticated_client, seeded_db):
    """Word records which user added it."""
    authenticated_client.post("/words/add", data={"word": "test"})

    word = Word.query.filter_by(word="test").first()
    assert word.user is not None
    assert word.user.username == "nick"


def test_dashboard_shows_word_count(authenticated_client, seeded_db):
    """Dashboard displays total word count."""
    # Add some words
    authenticated_client.post("/words/add", data={"word": "one"})
    authenticated_client.post("/words/add", data={"word": "two"})

    response = authenticated_client.get("/")

    assert response.status_code == 200
    assert b"2" in response.data


def test_add_word_empty_rejected(authenticated_client, seeded_db):
    """Empty word submission is rejected."""
    response = authenticated_client.post("/words/add", data={
        "word": ""
    }, follow_redirects=True)

    assert Word.query.count() == 0
    assert b"Please enter a word" in response.data


def test_add_word_whitespace_only_rejected(authenticated_client, seeded_db):
    """Whitespace-only word submission is rejected."""
    response = authenticated_client.post("/words/add", data={
        "word": "   "
    }, follow_redirects=True)

    assert Word.query.count() == 0


def test_add_word_with_category(authenticated_client, seeded_db):
    """Can add a word with a category."""
    from app.models import Category

    # First create a category
    from app import db
    category = Category(name="Noun", description="Things")
    db.session.add(category)
    db.session.commit()
    category_id = category.id

    response = authenticated_client.post("/words/add", data={
        "word": "ball",
        "category_id": str(category_id)
    }, follow_redirects=True)

    assert response.status_code == 200
    word = Word.query.filter_by(word="ball").first()
    assert word is not None
    assert word.category_id == category_id
