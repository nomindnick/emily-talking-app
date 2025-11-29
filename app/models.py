"""Database models for Emily Word Tracker."""

from datetime import datetime, timezone

import bcrypt
from sqlalchemy import func

from app import db


class User(db.Model):
    """User model for parent accounts."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)

    # Relationship to words
    words = db.relationship("Word", back_populates="user", lazy="dynamic")

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        """Verify password against stored hash."""
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def __repr__(self):
        return f"<User {self.username}>"


class Category(db.Model):
    """Category model for word classification."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)

    # Relationship to words
    words = db.relationship("Word", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


class Word(db.Model):
    """Word model for vocabulary tracking."""

    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    date_added = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = db.relationship("User", back_populates="words")
    category = db.relationship("Category", back_populates="words")

    def to_dict(self):
        """Serialize word to dictionary."""
        return {
            "id": self.id,
            "word": self.word,
            "date_added": self.date_added.isoformat() if self.date_added else None,
            "user_id": self.user_id,
            "user": self.user.display_name if self.user else None,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Word {self.word}>"
