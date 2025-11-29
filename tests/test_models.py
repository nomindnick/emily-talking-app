"""Tests for database models."""

import pytest

from app.models import Category, User, Word


class TestUserModel:
    """Tests for the User model."""

    def test_user_password_hashing(self, app):
        """User password hashing and verification works."""
        user = User(username="test", display_name="Test")
        user.set_password("secret123")
        assert user.check_password("secret123") is True
        assert user.check_password("wrong") is False

    def test_user_repr(self, app):
        """User has a readable string representation."""
        user = User(username="testuser", display_name="Test User")
        assert "testuser" in repr(user)


class TestCategoryModel:
    """Tests for the Category model."""

    def test_category_optional(self, app, db_session):
        """Word can be created without category."""
        # First create a user (required for word)
        user = User(username="test", display_name="Test")
        user.set_password("test")
        db_session.add(user)
        db_session.commit()

        # Create word without category
        word = Word(word="hello", user_id=user.id, category_id=None)
        db_session.add(word)
        db_session.commit()

        # Verify word was created without category
        assert word.id is not None
        assert word.category_id is None
        assert word.category is None

    def test_category_repr(self, app, db_session):
        """Category has a readable string representation."""
        category = Category(name="Noun", description="Things")
        db_session.add(category)
        db_session.commit()
        assert "Noun" in repr(category)


class TestWordModel:
    """Tests for the Word model."""

    def test_word_user_relationship(self, app, db_session):
        """Word correctly links to User."""
        user = User(username="test", display_name="Test")
        user.set_password("test")
        db_session.add(user)
        db_session.commit()

        word = Word(word="hello", user_id=user.id)
        db_session.add(word)
        db_session.commit()

        assert word.user.username == "test"

    def test_word_category_relationship(self, app, db_session):
        """Word correctly links to Category."""
        user = User(username="test", display_name="Test")
        user.set_password("test")
        db_session.add(user)

        category = Category(name="Noun", description="Things")
        db_session.add(category)
        db_session.commit()

        word = Word(word="ball", user_id=user.id, category_id=category.id)
        db_session.add(word)
        db_session.commit()

        assert word.category.name == "Noun"

    def test_word_to_dict(self, app, db_session):
        """Word.to_dict() returns correct structure."""
        user = User(username="test", display_name="Test User")
        user.set_password("test")
        db_session.add(user)

        category = Category(name="Verb", description="Actions")
        db_session.add(category)
        db_session.commit()

        word = Word(word="run", user_id=user.id, category_id=category.id)
        db_session.add(word)
        db_session.commit()

        word_dict = word.to_dict()

        # Verify all expected keys are present
        assert "id" in word_dict
        assert "word" in word_dict
        assert "date_added" in word_dict
        assert "user_id" in word_dict
        assert "user" in word_dict
        assert "category_id" in word_dict
        assert "category" in word_dict
        assert "created_at" in word_dict
        assert "updated_at" in word_dict

        # Verify values
        assert word_dict["word"] == "run"
        assert word_dict["user"] == "Test User"
        assert word_dict["category"] == "Verb"

    def test_word_to_dict_without_category(self, app, db_session):
        """Word.to_dict() handles missing category gracefully."""
        user = User(username="test", display_name="Test")
        user.set_password("test")
        db_session.add(user)
        db_session.commit()

        word = Word(word="hello", user_id=user.id)
        db_session.add(word)
        db_session.commit()

        word_dict = word.to_dict()
        assert word_dict["category"] is None
        assert word_dict["category_id"] is None

    def test_word_timestamps(self, app, db_session):
        """Word has automatic timestamps."""
        user = User(username="test", display_name="Test")
        user.set_password("test")
        db_session.add(user)
        db_session.commit()

        word = Word(word="test", user_id=user.id)
        db_session.add(word)
        db_session.commit()

        assert word.date_added is not None
        assert word.created_at is not None
        assert word.updated_at is not None

    def test_word_repr(self, app, db_session):
        """Word has a readable string representation."""
        user = User(username="test", display_name="Test")
        user.set_password("test")
        db_session.add(user)
        db_session.commit()

        word = Word(word="hello", user_id=user.id)
        db_session.add(word)
        db_session.commit()

        assert "hello" in repr(word)
