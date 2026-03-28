from __future__ import annotations

import pandas as pd

from churn_risk.features.build_features import (
    build_engineered_features,
    impute_total_charges,
    normalize_string_columns,
    select_feature_columns,
)


def test_feature_builder_creates_expected_columns() -> None:
    raw_df = pd.DataFrame(
        [
            {
                "customerID": "0001-TEST",
                "gender": "Female ",
                "SeniorCitizen": 1,
                "Partner": "Yes ",
                "Dependents": "No",
                "tenure": 6,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "Yes",
                "OnlineBackup": "No",
                "DeviceProtection": "Yes",
                "TechSupport": "No",
                "StreamingTV": "Yes",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 80.0,
                "TotalCharges": None,
                "Churn": 1,
            }
        ]
    )

    normalized = normalize_string_columns(raw_df)
    enriched = impute_total_charges(normalized)
    featured = build_engineered_features(enriched)
    selected = select_feature_columns(featured)

    row = selected.iloc[0]

    assert row["gender"] == "Female"
    assert row["Partner"] == "Yes"
    assert row["TotalCharges"] == 480.0
    assert row["tenure_bucket"] == "0_12"
    assert row["contract_term_months"] == 1
    assert row["has_internet"] == 1
    assert row["has_security"] == 1
    assert row["payment_risk_flag"] == 1
    assert row["is_senior"] == 1
    assert row["has_partner"] == 1
    assert row["has_dependents"] == 0
    assert row["churn_flag"] == 1
