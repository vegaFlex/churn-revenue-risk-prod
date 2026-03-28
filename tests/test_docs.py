from __future__ import annotations

from fastapi.testclient import TestClient

from churn_risk.api.app import app


def test_documentation_routes_render() -> None:
    client = TestClient(app)

    for route in ["/docs/guide/", "/docs/user-guide/", "/docs/manual-testing-guide/", "/docs/buyer-guide/", "/docs/upload-schema-guide/"]:
        response = client.get(route)
        assert response.status_code == 200

    hub = client.get("/docs/guide/")
    assert "Documentation Center" in hub.text

    user_guide = client.get("/docs/user-guide/")
    assert "User Guide" in user_guide.text
