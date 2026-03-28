from __future__ import annotations

import pandas as pd

from churn_risk.ui.upload_service import (
    apply_column_mapping,
    build_dataset_profile,
    suggest_schema_mapping,
)


def test_schema_mapping_suggests_known_synonyms() -> None:
    df = pd.DataFrame(
        [
            {
                "client_id": "0001-TEST",
                "sex": "Female",
                "senior_flag": 0,
                "partner_flag": "Yes",
                "dependent_flag": "No",
                "months_active": 12,
                "phone_service": "Yes",
                "multiple_lines": "No",
                "internet_type": "Fiber optic",
                "online_security": "No",
                "online_backup": "Yes",
                "device_protection": "No",
                "tech_support": "No",
                "streaming_tv": "Yes",
                "streaming_movies": "Yes",
                "contract_type": "Month-to-month",
                "paperless_billing": "Yes",
                "billing_method": "Electronic check",
                "monthly_fee": 89.45,
                "total_billed": 1073.40,
            }
        ]
    )

    suggestions = suggest_schema_mapping(df.columns.tolist())

    assert suggestions["customerID"] == "client_id"
    assert suggestions["gender"] == "sex"
    assert suggestions["tenure"] == "months_active"
    assert suggestions["MonthlyCharges"] == "monthly_fee"
    assert suggestions["TotalCharges"] == "total_billed"


def test_apply_column_mapping_renames_uploaded_columns() -> None:
    df = pd.DataFrame(
        [
            {
                "client_id": "0001-TEST",
                "monthly_fee": 89.45,
                "contract_type": "Month-to-month",
            }
        ]
    )

    mapped = apply_column_mapping(
        df,
        {
            "customerID": "client_id",
            "MonthlyCharges": "monthly_fee",
            "Contract": "contract_type",
        },
    )

    assert "customerID" in mapped.columns
    assert "MonthlyCharges" in mapped.columns
    assert "Contract" in mapped.columns


def test_dataset_profile_counts_suggested_matches() -> None:
    df = pd.DataFrame(
        [
            {
                "client_id": "0001-TEST",
                "monthly_fee": 89.45,
                "contract_type": "Month-to-month",
                "billing_method": "Electronic check",
            }
        ]
    )

    profile = build_dataset_profile(df)

    assert profile["rows"] == 1
    assert profile["columns"] == 4
    assert profile["mapped_fields"] >= 3
