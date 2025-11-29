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


def check_duplicate_word_excluding(word_text, exclude_id):
    """Check if a word already exists, excluding a specific word ID.

    Used for edit validation to check duplicates against OTHER words.

    Args:
        word_text: The word to check for duplicates.
        exclude_id: The word ID to exclude from the check (the word being edited).

    Returns:
        The existing Word if a duplicate is found, None otherwise.
    """
    return Word.query.filter(
        func.lower(Word.word) == word_text.lower().strip(),
        Word.id != exclude_id
    ).first()
