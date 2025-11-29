"""Utility functions for Emily Word Tracker."""

import calendar
from datetime import date

from sqlalchemy import extract, func

from app.models import Word
from app.milestones import get_milestone_for_age as _get_milestone_for_age


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


def calculate_age_months(birthdate, reference_date=None):
    """Calculate age in months from birthdate to reference date.

    Args:
        birthdate: The date of birth (date object).
        reference_date: The date to calculate age at. Defaults to today.

    Returns:
        Age in months as an integer.
    """
    if reference_date is None:
        reference_date = date.today()

    months = (reference_date.year - birthdate.year) * 12
    months += reference_date.month - birthdate.month

    # Adjust if we haven't reached the birthday day yet this month
    if reference_date.day < birthdate.day:
        months -= 1

    return max(0, months)


def get_milestone_for_age(months):
    """Get the developmental milestone for a given age.

    Wrapper around milestones module function.

    Args:
        months: Age in months.

    Returns:
        Milestone dictionary or None.
    """
    return _get_milestone_for_age(months)


def group_words_by_month(words):
    """Group a list of words by the month they were added.

    Args:
        words: List of Word objects.

    Returns:
        Dictionary with (year, month) tuples as keys and lists of words as values.
    """
    grouped = {}
    for word in words:
        if word.date_added:
            key = (word.date_added.year, word.date_added.month)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(word)
    return grouped


def get_monthly_stats():
    """Get word counts grouped by month with running totals.

    Returns:
        List of dictionaries with year, month, month_name, count, running_total.
        Sorted from oldest to newest.
    """
    # Query to group words by year and month
    results = (
        Word.query.with_entities(
            extract("year", Word.date_added).label("year"),
            extract("month", Word.date_added).label("month"),
            func.count(Word.id).label("count"),
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    monthly_stats = []
    running_total = 0

    for row in results:
        running_total += row.count
        monthly_stats.append({
            "year": int(row.year),
            "month": int(row.month),
            "month_name": calendar.month_name[int(row.month)],
            "count": row.count,
            "running_total": running_total,
        })

    return monthly_stats