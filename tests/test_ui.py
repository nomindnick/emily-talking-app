"""Tests for UI/CSS and Sprint 8 features."""


def test_static_css_exists(client):
    """CSS files are served from static directory."""
    response = client.get("/static/css/style.css")
    assert response.status_code == 200


def test_css_tokens_exist(client):
    """CSS tokens file exists and contains custom properties."""
    response = client.get("/static/css/tokens.css")
    assert response.status_code == 200
    assert b"--color-primary" in response.data
    assert b"--space-" in response.data


def test_css_components_exist(client):
    """CSS components file exists."""
    response = client.get("/static/css/components.css")
    assert response.status_code == 200


def test_dashboard_shows_recent_words(authenticated_client, seeded_db, sample_words):
    """Dashboard shows recent words preview."""
    response = authenticated_client.get("/")
    assert response.status_code == 200
    assert b"Recently Added" in response.data
    # Check that at least one recent word is visible
    assert any(w.word.encode() in response.data for w in sample_words[-5:])


def test_responsive_viewport_meta(authenticated_client, seeded_db):
    """Pages include viewport meta tag."""
    response = authenticated_client.get("/")
    assert b"viewport" in response.data
    assert b"width=device-width" in response.data


def test_flash_messages_have_close_button(authenticated_client, seeded_db):
    """Flash messages include close button."""
    # Add a word to trigger success flash
    authenticated_client.post("/words/add", data={"word": "testword"})
    response = authenticated_client.get("/", follow_redirects=True)
    assert b"flash-close" in response.data


def test_css_link_in_base_template(authenticated_client, seeded_db):
    """Base template links to external stylesheet."""
    response = authenticated_client.get("/")
    assert b"/static/css/style.css" in response.data


def test_login_page_loads_without_css_errors(client):
    """Login page loads with external CSS (no inline styles)."""
    response = client.get("/login")
    assert response.status_code == 200
    # Should reference external stylesheet
    assert b"/static/css/style.css" in response.data
    # Should NOT have large inline style blocks
    # (small style blocks might still exist, but not the full component styles)
    style_count = response.data.count(b"<style>")
    assert style_count == 0, f"Found {style_count} inline style blocks"


def test_word_list_page_loads(authenticated_client, seeded_db, sample_words):
    """Word list page loads correctly."""
    response = authenticated_client.get("/words")
    assert response.status_code == 200
    # Should have word table and word cards classes from CSS
    assert b"word-table" in response.data
    assert b"word-cards" in response.data


def test_stats_page_loads(authenticated_client, seeded_db, sample_words):
    """Stats page loads correctly."""
    response = authenticated_client.get("/stats")
    assert response.status_code == 200
    assert b"Statistics" in response.data
    # Should have stat-card class from CSS
    assert b"stat-card" in response.data


def test_edit_word_page_loads(authenticated_client, seeded_db, sample_words):
    """Edit word page loads correctly."""
    word = sample_words[0]
    response = authenticated_client.get(f"/words/{word.id}/edit")
    assert response.status_code == 200
    # Should have edit-section and danger-zone classes from CSS
    assert b"edit-section" in response.data
    assert b"danger-zone" in response.data
