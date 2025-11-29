"""Basic application tests."""


def test_app_exists(app):
    """App factory creates app instance."""
    assert app is not None


def test_app_runs(client):
    """App responds to requests."""
    # Root route is protected, so check login page instead
    response = client.get("/login")
    assert response.status_code == 200
