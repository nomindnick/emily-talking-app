"""Basic application tests."""


def test_app_exists(app):
    """App factory creates app instance."""
    assert app is not None


def test_app_runs(client):
    """App responds to requests."""
    response = client.get("/")
    assert response.status_code == 200
