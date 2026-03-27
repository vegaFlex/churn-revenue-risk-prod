from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from churn_risk.config import settings


STRING_COLUMNS = [
    "customerID",
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
]


def load_raw_dataset(parquet_path: str) -> pd.DataFrame:
    source = Path(parquet_path)
    if not source.exists():
        raise FileNotFoundError(f"Raw parquet dataset not found: {source}")

    return pd.read_parquet(source)


def normalize_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()

    for column in STRING_COLUMNS:
        normalized[column] = normalized[column].astype(str).str.strip()

    return normalized


def impute_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    estimated_total = enriched["MonthlyCharges"] * enriched["tenure"]
    enriched["TotalCharges"] = enriched["TotalCharges"].fillna(estimated_total)
    return enriched


def build_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    features = df.copy()

    features["churn_flag"] = features["Churn"].astype("int64")
    features["tenure_bucket"] = pd.cut(
        features["tenure"],
        bins=[-1, 12, 24, 48, 72],
        labels=["0_12", "13_24", "25_48", "49_72"],
    ).astype(str)
    features["contract_term_months"] = features["Contract"].map(
        {
            "Month-to-month": 1,
            "One year": 12,
            "Two year": 24,
        }
    ).astype("int64")
    features["monthly_charges_log"] = np.log1p(features["MonthlyCharges"])
    features["has_internet"] = (features["InternetService"] != "No").astype("int64")
    features["has_security"] = (features["OnlineSecurity"] == "Yes").astype("int64")
    features["payment_risk_flag"] = (
        features["PaymentMethod"] == "Electronic check"
    ).astype("int64")
    features["is_senior"] = features["SeniorCitizen"].astype("int64")
    features["has_partner"] = (features["Partner"] == "Yes").astype("int64")
    features["has_dependents"] = (features["Dependents"] == "Yes").astype("int64")

    return features


def select_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    selected_columns = [
        "customerID",
        "gender",
        "SeniorCitizen",
        "Partner",
        "Dependents",
        "tenure",
        "PhoneService",
        "MultipleLines",
        "InternetService",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
        "Contract",
        "PaperlessBilling",
        "PaymentMethod",
        "MonthlyCharges",
        "TotalCharges",
        "churn_flag",
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
    return df[selected_columns].copy()


def save_features(df: pd.DataFrame, output_path: str) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destination, index=False)
    print(f"Saved feature dataset to {destination}")


def main() -> None:
    raw_df = load_raw_dataset(settings.parquet_raw_path)
    normalized_df = normalize_string_columns(raw_df)
    enriched_df = impute_total_charges(normalized_df)
    feature_df = build_engineered_features(enriched_df)
    output_df = select_feature_columns(feature_df)
    save_features(df=output_df, output_path=settings.features_path)


if __name__ == "__main__":
    main()
