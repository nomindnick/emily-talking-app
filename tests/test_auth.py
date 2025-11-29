"""Authentication tests for Sprint 2."""

import pytest


def test_login_page_loads(client):
    """Login page is accessible."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"password" in response.data.lower()


def test_login_success(client, seeded_db):
    """Valid credentials log user in."""
    response = client.post("/login", data={
        "username": "nick",
        "password": "testpass"
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to dashboard, show welcome message
    assert b"Welcome back" in response.data or b"Nick" in response.data


def test_login_failure(client, seeded_db):
    """Invalid password rejected."""
    response = client.post("/login", data={
        "username": "nick",
        "password": "wrongpass"
    }, follow_redirects=True)
    assert b"invalid" in response.data.lower() or b"Invalid" in response.data


def test_protected_route_redirects(client):
    """Unauthenticated user redirected to login."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location


def test_logout(authenticated_client):
    """Logout clears session."""
    response = authenticated_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    # After logout, accessing protected route should redirect
    response = authenticated_client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location
