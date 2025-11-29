"""Tests for statistics page and functionality."""

import pytest


def test_stats_page_loads(authenticated_client, seeded_db):
    """Stats page loads for authenticated user."""
    response = authenticated_client.get("/stats")
    assert response.status_code == 200
    assert b"Statistics" in response.data


def test_stats_requires_auth(client):
    """Stats page redirects to login when not authenticated."""
    response = client.get("/stats")
    assert response.status_code == 302
    assert "/login" in response.location


def test_total_count_accurate(authenticated_client, seeded_db, sample_words):
    """Stats shows correct total word count."""
    response = authenticated_client.get("/stats")
    assert response.status_code == 200
    expected_count = str(len(sample_words))
    assert expected_count.encode() in response.data


def test_stats_shows_milestones(authenticated_client, seeded_db):
    """Stats page displays developmental milestones."""
    response = authenticated_client.get("/stats")
    assert response.status_code == 200
    # Check for milestone labels
    assert b"12 months" in response.data
    assert b"18 months" in response.data
    assert b"24 months" in response.data


def test_stats_shows_monthly_breakdown(authenticated_client, seeded_db, sample_words):
    """Stats page shows monthly word breakdown when words exist."""
    response = authenticated_client.get("/stats")
    assert response.status_code == 200
    # Should show "Words by Month" section
    assert b"Words by Month" in response.data
    # Should show running total header
    assert b"Running Total" in response.data


def test_stats_empty_monthly_message(authenticated_client, seeded_db):
    """Stats page shows message when no words exist."""
    response = authenticated_client.get("/stats")
    assert response.status_code == 200
    # Should show the no-data message
    assert b"No words added yet" in response.data


def test_stats_with_baby_birthdate(app, authenticated_client, seeded_db):
    """Stats shows baby age when BABY_BIRTHDATE is configured."""
    # Set a birthdate in the config
    app.config["BABY_BIRTHDATE"] = "2024-01-15"

    response = authenticated_client.get("/stats")
    assert response.status_code == 200
    # Should show age display
    assert b"months" in response.data
    # Should show Emily's Age section
    assert b"Emily" in response.data or b"Age" in response.data


def test_stats_without_baby_birthdate(app, authenticated_client, seeded_db):
    """Stats works correctly without BABY_BIRTHDATE configured."""
    # Ensure no birthdate is set
    app.config["BABY_BIRTHDATE"] = None

    response = authenticated_client.get("/stats")
    assert response.status_code == 200
    # Should still load successfully
    assert b"Statistics" in response.data
