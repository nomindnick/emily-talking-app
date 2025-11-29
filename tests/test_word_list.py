"""Tests for word list functionality (Sprint 4)."""

import pytest

from app.models import Word


class TestWordListDisplay:
    """Tests for basic word list page functionality."""

    def test_word_list_displays(self, authenticated_client, sample_words):
        """Word list page shows all words."""
        response = authenticated_client.get("/words")
        assert response.status_code == 200

        # All sample words should be visible
        for word in sample_words:
            assert word.word.encode() in response.data

    def test_word_list_requires_auth(self, client):
        """Word list page requires authentication."""
        response = client.get("/words")
        assert response.status_code == 302
        assert "/login" in response.location


class TestWordListSorting:
    """Tests for sorting functionality."""

    def test_sort_alphabetical_asc(self, authenticated_client, sample_words):
        """Words can be sorted A-Z."""
        response = authenticated_client.get("/words?sort=word&order=asc")
        assert response.status_code == 200

        # Get the response data - look at table only (first instance)
        data = response.data.decode("utf-8")

        # Find positions in the table section (before word-cards div)
        table_section = data.split('class="word-cards"')[0]

        # Verify order: apple should come before banana, banana before cat, etc.
        apple_pos = table_section.find(">apple<")
        banana_pos = table_section.find(">banana<")
        cat_pos = table_section.find(">cat<")
        dog_pos = table_section.find(">dog<")
        eat_pos = table_section.find(">eat<")

        assert apple_pos < banana_pos < cat_pos < dog_pos < eat_pos

    def test_sort_alphabetical_desc(self, authenticated_client, sample_words):
        """Words can be sorted Z-A."""
        response = authenticated_client.get("/words?sort=word&order=desc")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        table_section = data.split('class="word-cards"')[0]

        # Verify reverse order: eat should come before dog, dog before cat, etc.
        apple_pos = table_section.find(">apple<")
        banana_pos = table_section.find(">banana<")
        cat_pos = table_section.find(">cat<")
        dog_pos = table_section.find(">dog<")
        eat_pos = table_section.find(">eat<")

        assert eat_pos < dog_pos < cat_pos < banana_pos < apple_pos

    def test_sort_by_date_desc(self, authenticated_client, sample_words):
        """Words can be sorted by date (newest first)."""
        response = authenticated_client.get("/words?sort=date&order=desc")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        table_section = data.split('class="word-cards"')[0]

        # Order should be: dog (1 day ago), cat (3 days), banana (5 days),
        # eat (7 days), apple (10 days)
        dog_pos = table_section.find(">dog<")
        cat_pos = table_section.find(">cat<")
        banana_pos = table_section.find(">banana<")
        eat_pos = table_section.find(">eat<")
        apple_pos = table_section.find(">apple<")

        assert dog_pos < cat_pos < banana_pos < eat_pos < apple_pos

    def test_sort_by_date_asc(self, authenticated_client, sample_words):
        """Words can be sorted by date (oldest first)."""
        response = authenticated_client.get("/words?sort=date&order=asc")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        table_section = data.split('class="word-cards"')[0]

        # Order should be: apple (oldest), eat, banana, cat, dog (newest)
        dog_pos = table_section.find(">dog<")
        cat_pos = table_section.find(">cat<")
        banana_pos = table_section.find(">banana<")
        eat_pos = table_section.find(">eat<")
        apple_pos = table_section.find(">apple<")

        assert apple_pos < eat_pos < banana_pos < cat_pos < dog_pos


class TestWordListFiltering:
    """Tests for filtering functionality."""

    def test_filter_by_category(self, authenticated_client, sample_words):
        """Words can be filtered by category."""
        # Find the noun category ID (apple, banana, dog are nouns)
        from app.models import Category

        noun = Category.query.filter_by(name="Noun").first()

        response = authenticated_client.get(f"/words?category={noun.id}")
        assert response.status_code == 200

        data = response.data.decode("utf-8")

        # Nouns should be present
        assert "apple" in data
        assert "banana" in data
        assert "dog" in data

        # Non-nouns should not be present (cat has no category, eat is verb)
        # Note: cat has no category so won't be in noun filter
        assert "eat" not in data

    def test_filter_by_user(self, authenticated_client, sample_words):
        """Words can be filtered by user who added them."""
        from app.models import User

        nick = User.query.filter_by(username="nick").first()

        response = authenticated_client.get(f"/words?user={nick.id}")
        assert response.status_code == 200

        data = response.data.decode("utf-8")

        # Nick's words should be present (apple, cat, eat)
        assert "apple" in data
        assert "cat" in data
        assert "eat" in data

        # Wife's words should not be present (banana, dog)
        assert "banana" not in data
        assert "dog" not in data

    def test_filter_combined(self, authenticated_client, sample_words):
        """Multiple filters can be combined."""
        from app.models import Category, User

        noun = Category.query.filter_by(name="Noun").first()
        nick = User.query.filter_by(username="nick").first()

        response = authenticated_client.get(
            f"/words?category={noun.id}&user={nick.id}"
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        table_section = data.split('class="word-cards"')[0]

        # Only apple is a noun added by Nick
        assert ">apple<" in table_section

        # These are nouns but added by wife
        assert ">banana<" not in table_section
        assert ">dog<" not in table_section

        # These are by nick but not nouns
        assert ">cat<" not in table_section  # no category
        assert ">eat<" not in table_section  # verb


class TestWordListNavigation:
    """Tests for navigation links."""

    def test_dashboard_has_word_list_link(self, authenticated_client, seeded_db):
        """Dashboard has a link to word list."""
        response = authenticated_client.get("/")
        assert response.status_code == 200
        assert b"/words" in response.data

    def test_nav_has_word_list_link(self, authenticated_client, seeded_db):
        """Navigation has a link to word list."""
        response = authenticated_client.get("/")
        assert b"Word List" in response.data
