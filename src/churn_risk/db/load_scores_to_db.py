from __future__ import annotations

import pandas as pd

from churn_risk.config import settings
from churn_risk.db.base import engine


def build_scores_payload() -> pd.DataFrame:
    df = pd.read_parquet(settings.scores_path).copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"]).dt.date
    return df.rename(
        columns={
            "customerID": "customer_id",
            "SeniorCitizen": "senior_citizen",
            "Partner": "partner",
            "Dependents": "dependents",
            "InternetService": "internet_service",
            "Contract": "contract",
            "PaymentMethod": "payment_method",
            "MonthlyCharges": "monthly_charges",
            "TotalCharges": "total_charges",
        }
    )[
        [
            "snapshot_date",
            "customer_id",
            "gender",
            "senior_citizen",
            "partner",
            "dependents",
            "tenure",
            "internet_service",
            "contract",
            "payment_method",
            "monthly_charges",
            "total_charges",
            "churn_probability",
            "monthly_revenue",
            "expected_months_remaining",
            "revenue_at_risk",
            "risk_segment",
            "churn_flag",
        ]
    ]


def main() -> None:
    payload = build_scores_payload()
    payload.to_sql("scores_daily", engine, if_exists="replace", index=False)
    print(f"Loaded {len(payload)} rows into scores_daily")


if __name__ == "__main__":
    main()
