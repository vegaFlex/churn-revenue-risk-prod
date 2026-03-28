from __future__ import annotations

from fastapi.testclient import TestClient

from churn_risk.api.app import app


def test_login_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/login")
    assert response.status_code == 200
    assert "Sign in to the platform" in response.text


def test_upload_redirects_when_not_logged_in() -> None:
    client = TestClient(app)
    response = client.get("/upload", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_page_only_exposes_public_viewer_account() -> None:
    client = TestClient(app)
    response = client.get("/login")
    assert response.status_code == 200
    assert "viewer_demo" in response.text
    assert "ViewerPass123!" in response.text
    assert "Read-only reviewer account" in response.text
    assert "analyst_demo" not in response.text
    assert "admin_demo" not in response.text
