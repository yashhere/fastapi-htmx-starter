from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    """Test that the app starts successfully."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "FastAPI HTMX Starter" in response.text


def test_login_page():
    """Test that the login page loads."""
    with TestClient(app) as client:
        response = client.get("/login")
        assert response.status_code == 200
        assert "Login" in response.text


def test_register_page():
    """Test that the register page loads."""
    with TestClient(app) as client:
        response = client.get("/register")
        assert response.status_code == 200
        assert "Create Account" in response.text


def test_items_requires_auth():
    """Test that items page requires authentication."""
    with TestClient(app) as client:
        response = client.get("/items")
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
