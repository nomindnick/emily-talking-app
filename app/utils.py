"""Utility functions for Emily Word Tracker."""

from sqlalchemy import func

from app.models import Word


def check_duplicate_word(word_text):
    """Check if a word already exists (case-insensitive).

    Args:
        word_text: The word to check for duplicates.

    Returns:
        The existing Word if a duplicate is found, None otherwise.
    """
    return Word.query.filter(
        func.lower(Word.word) == word_text.lower().strip()
    ).first()
