from __future__ import annotations

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from churn_risk.api import app as app_module
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


def test_admin_route_requires_admin_role(monkeypatch: MonkeyPatch) -> None:
    client = TestClient(app)

    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    monkeypatch.setattr(
        app_module,
        "get_current_user",
        lambda request: {"user_id": 1, "username": "viewer_demo", "role": "viewer"},
    )
    response = client.get("/admin")
    assert response.status_code == 403
    assert "Admin controls are restricted to authorised internal users." in response.text


def test_admin_action_runs_for_admin(monkeypatch: MonkeyPatch) -> None:
    client = TestClient(app)

    monkeypatch.setattr(
        app_module,
        "get_current_user",
        lambda request: {"user_id": 99, "username": "admin_demo", "role": "admin"},
    )
    monkeypatch.setattr(
        app_module,
        "build_admin_context",
        lambda notice_message=None, notice_tone="info": {
            "page_title": "Admin Controls",
            "control_cards": [],
            "registry_rows": [],
            "allowed_actions": [],
            "planned_actions": [],
            "action_cards": [],
            "admin_notice_message": notice_message,
            "admin_notice_tone": notice_tone,
        },
    )
    monkeypatch.setattr(app_module, "run_data_drift_job", lambda: None)
    monkeypatch.setattr(app_module, "run_prediction_drift_job", lambda: None)
    monkeypatch.setattr(app_module, "run_threshold_alert_job", lambda: None)

    response = client.post("/admin/actions", data={"action_name": "run_monitoring"})
    assert response.status_code == 200
    assert "Monitoring suite completed successfully." in response.text
