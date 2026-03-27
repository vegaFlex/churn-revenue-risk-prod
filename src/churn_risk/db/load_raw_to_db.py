from __future__ import annotations

import pandas as pd

from churn_risk.config import settings
from churn_risk.db.base import engine


def build_raw_payload() -> pd.DataFrame:
    df = pd.read_parquet(settings.parquet_raw_path).copy()
    df["churn_flag"] = df["Churn"].astype("int64")
    return df.rename(
        columns={
            "customerID": "customer_id",
            "SeniorCitizen": "senior_citizen",
            "PhoneService": "phone_service",
            "MultipleLines": "multiple_lines",
            "InternetService": "internet_service",
            "OnlineSecurity": "online_security",
            "OnlineBackup": "online_backup",
            "DeviceProtection": "device_protection",
            "TechSupport": "tech_support",
            "StreamingTV": "streaming_tv",
            "StreamingMovies": "streaming_movies",
            "Contract": "contract",
            "PaperlessBilling": "paperless_billing",
            "PaymentMethod": "payment_method",
            "MonthlyCharges": "monthly_charges",
            "TotalCharges": "total_charges",
            "Partner": "partner",
            "Dependents": "dependents",
            "gender": "gender",
        }
    )[
        [
            "customer_id",
            "gender",
            "senior_citizen",
            "partner",
            "dependents",
            "tenure",
            "phone_service",
            "multiple_lines",
            "internet_service",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
            "contract",
            "paperless_billing",
            "payment_method",
            "monthly_charges",
            "total_charges",
            "churn_flag",
        ]
    ]


def main() -> None:
    raw_payload = build_raw_payload()
    raw_payload.to_sql("customers_raw", engine, if_exists="replace", index=False)
    print(f"Loaded {len(raw_payload)} rows into customers_raw")


if __name__ == "__main__":
    main()
