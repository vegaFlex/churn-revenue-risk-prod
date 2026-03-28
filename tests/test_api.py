from __future__ import annotations

from fastapi.testclient import TestClient

from churn_risk.api.app import app


def test_score_endpoint_returns_expected_payload() -> None:
    client = TestClient(app)

    payload = {
        "customerID": "7590-VHVEG",
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "No",
        "MultipleLines": "No phone service",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 29.85,
        "TotalCharges": 29.85,
    }

    response = client.post("/score", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["customer_id"] == "7590-VHVEG"
    assert 0 <= body["churn_probability"] <= 1
    assert body["risk_segment"] in {"low", "medium", "high"}
    assert body["revenue_at_risk"] >= 0
    assert body["expected_months_remaining"] >= 1
