"""Tests for word edit and delete functionality (Sprint 5)."""

import time

from app.models import Word


def test_edit_form_loads(authenticated_client, seeded_db, sample_words):
    """Edit form loads with word data."""
    word = sample_words[0]
    response = authenticated_client.get(f"/words/{word.id}/edit")
    assert response.status_code == 200
    assert word.word.encode() in response.data


def test_edit_word_text(authenticated_client, seeded_db, sample_words):
    """Can edit word text."""
    word = sample_words[0]
    response = authenticated_client.post(f"/words/{word.id}/edit", data={
        "word": "updated_word",
        "category_id": word.category_id or ""
    }, follow_redirects=True)
    assert response.status_code == 200
    updated = Word.query.get(word.id)
    assert updated.word == "updated_word"


def test_edit_updates_timestamp(authenticated_client, seeded_db, sample_words):
    """Editing word updates updated_at."""
    word = sample_words[0]
    original_updated = word.updated_at

    # Small delay to ensure timestamp difference
    time.sleep(0.1)

    authenticated_client.post(f"/words/{word.id}/edit", data={
        "word": "changed"
    })
    updated = Word.query.get(word.id)
    assert updated.updated_at > original_updated


def test_edit_duplicate_rejected(authenticated_client, seeded_db, sample_words):
    """Cannot edit word to duplicate another word."""
    word1, word2 = sample_words[0], sample_words[1]
    original_word1_text = word1.word

    response = authenticated_client.post(f"/words/{word1.id}/edit", data={
        "word": word2.word  # Try to rename to existing word
    }, follow_redirects=True)

    # Should reject, word1 should be unchanged
    updated = Word.query.get(word1.id)
    assert updated.word == original_word1_text


def test_delete_word(authenticated_client, seeded_db, sample_words):
    """Can delete a word."""
    word = sample_words[0]
    word_id = word.id

    response = authenticated_client.post(f"/words/{word_id}/delete",
                                         follow_redirects=True)
    assert response.status_code == 200
    assert Word.query.get(word_id) is None
