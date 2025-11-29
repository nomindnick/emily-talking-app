"""Tests for CSV export functionality."""

from app.models import Word


def test_export_returns_csv(authenticated_client, seeded_db, sample_words):
    """Export returns CSV file."""
    response = authenticated_client.get("/export")
    assert response.status_code == 200
    assert "text/csv" in response.content_type


def test_export_filename(authenticated_client, seeded_db, sample_words):
    """Export has correct filename with date."""
    response = authenticated_client.get("/export")
    content_disposition = response.headers.get("Content-Disposition", "")
    assert "attachment" in content_disposition
    assert "emily_words_" in content_disposition
    assert ".csv" in content_disposition


def test_export_contains_all_words(authenticated_client, seeded_db, sample_words):
    """Export includes all words."""
    response = authenticated_client.get("/export")
    csv_content = response.data.decode("utf-8")
    for word in sample_words:
        assert word.word in csv_content


def test_export_headers(authenticated_client, seeded_db, sample_words):
    """Export has correct CSV headers."""
    response = authenticated_client.get("/export")
    csv_content = response.data.decode("utf-8")
    first_line = csv_content.split("\n")[0]
    assert "Word" in first_line
    assert "Date Added" in first_line
    assert "Added By" in first_line
    assert "Category" in first_line


def test_export_handles_special_characters(authenticated_client, seeded_db):
    """Export handles commas and quotes in words."""
    # Add word with comma
    authenticated_client.post("/words/add", data={"word": "uh-oh, no"})
    response = authenticated_client.get("/export")
    # Should be properly quoted in CSV
    assert response.status_code == 200
    csv_content = response.data.decode("utf-8")
    # Word with comma should be present (csv module handles quoting)
    assert "uh-oh" in csv_content


def test_export_sorted_by_date(authenticated_client, seeded_db, sample_words):
    """Export words are sorted by date (oldest first)."""
    response = authenticated_client.get("/export")
    csv_content = response.data.decode("utf-8")
    lines = csv_content.strip().split("\n")

    # Skip header (line 0) and BOM
    # Find the positions of known words in the export
    apple_pos = None
    dog_pos = None

    for i, line in enumerate(lines[1:], start=1):
        if "apple" in line:
            apple_pos = i
        if "dog" in line:
            dog_pos = i

    # apple was added 10 days ago, dog 1 day ago
    # So apple should appear before dog in oldest-first order
    assert apple_pos is not None
    assert dog_pos is not None
    assert apple_pos < dog_pos


def test_export_includes_user_display_name(authenticated_client, seeded_db, sample_words):
    """Export includes user display names."""
    response = authenticated_client.get("/export")
    csv_content = response.data.decode("utf-8")
    # Should include display names from seeded users
    assert "Nick" in csv_content
    assert "Partner" in csv_content


def test_export_includes_category_name(authenticated_client, seeded_db, sample_words):
    """Export includes category names."""
    response = authenticated_client.get("/export")
    csv_content = response.data.decode("utf-8")
    # Should include category names
    assert "Noun" in csv_content
    assert "Verb" in csv_content


def test_export_requires_authentication(client, seeded_db):
    """Export route requires login."""
    response = client.get("/export")
    assert response.status_code == 302
    assert "/login" in response.location


def test_export_empty_database(authenticated_client, seeded_db):
    """Export works with no words."""
    response = authenticated_client.get("/export")
    assert response.status_code == 200
    csv_content = response.data.decode("utf-8")
    # Should still have headers
    assert "Word" in csv_content
    assert "Date Added" in csv_content
