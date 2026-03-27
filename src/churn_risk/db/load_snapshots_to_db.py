from __future__ import annotations

import pandas as pd

from churn_risk.config import settings
from churn_risk.db.base import engine


def build_snapshot_payload() -> pd.DataFrame:
    df = pd.read_parquet(settings.customer_snapshots_path).copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"]).dt.date
    return df.rename(
        columns={
            "customerID": "customer_id",
            "SeniorCitizen": "senior_citizen",
            "Partner": "partner",
            "Dependents": "dependents",
            "Contract": "contract",
            "PaymentMethod": "payment_method",
            "InternetService": "internet_service",
        }
    )


def main() -> None:
    payload = build_snapshot_payload()
    payload.to_sql("customer_snapshots", engine, if_exists="replace", index=False)
    print(f"Loaded {len(payload)} rows into customer_snapshots")


if __name__ == "__main__":
    main()
