from __future__ import annotations

import pandas as pd

from churn_risk.config import settings
from churn_risk.db.base import engine


def build_feature_payload() -> pd.DataFrame:
    df = pd.read_parquet(settings.features_path).copy()
    return df.rename(
        columns={
            "customerID": "customer_id",
        }
    )[
        [
            "customer_id",
            "tenure_bucket",
            "contract_term_months",
            "monthly_charges_log",
            "has_internet",
            "has_security",
            "payment_risk_flag",
            "is_senior",
            "has_partner",
            "has_dependents",
        ]
    ]


def main() -> None:
    payload = build_feature_payload()
    payload.to_sql("features", engine, if_exists="replace", index=False)
    print(f"Loaded {len(payload)} rows into features")


if __name__ == "__main__":
    main()
