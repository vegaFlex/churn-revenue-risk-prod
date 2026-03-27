from __future__ import annotations

from pathlib import Path

import pandas as pd

from churn_risk.config import settings


REQUIRED_COLUMNS = [
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
    "Churn",
]


def load_raw_dataset(csv_path: str) -> pd.DataFrame:
    source = Path(csv_path)
    if not source.exists():
        raise FileNotFoundError(f"Raw dataset not found: {source}")

    return pd.read_csv(source)


def clean_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["TotalCharges"] = pd.to_numeric(cleaned["TotalCharges"], errors="coerce")
    return cleaned


def validate_schema(df: pd.DataFrame) -> None:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def validate_row_count(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("Dataset is empty.")

    if len(df) < 1000:
        raise ValueError(f"Unexpectedly low row count: {len(df)}")


def validate_duplicates(df: pd.DataFrame) -> None:
    duplicate_customer_ids = df["customerID"].duplicated().sum()
    if duplicate_customer_ids > 0:
        raise ValueError(f"Found duplicate customerID values: {duplicate_customer_ids}")


def validate_missing_values(df: pd.DataFrame) -> None:
    critical_columns = ["customerID", "tenure", "MonthlyCharges", "Churn"]
    missing_summary = df[critical_columns].isna().sum()

    if missing_summary.any():
        raise ValueError(f"Critical missing values detected: {missing_summary.to_dict()}")


def validate_business_ranges(df: pd.DataFrame) -> None:
    tenure_min = int(df["tenure"].min())
    tenure_max = int(df["tenure"].max())
    monthly_min = float(df["MonthlyCharges"].min())
    monthly_max = float(df["MonthlyCharges"].max())

    if tenure_min < 0 or tenure_max > 72:
        raise ValueError(f"Unexpected tenure range: min={tenure_min}, max={tenure_max}")

    if monthly_min < 0 or monthly_max <= 0:
        raise ValueError(
            f"Unexpected MonthlyCharges range: min={monthly_min:.2f}, max={monthly_max:.2f}"
        )


def validate_target_values(df: pd.DataFrame) -> None:
    allowed_values = {"Yes", "No"}
    actual_values = set(df["Churn"].dropna().unique())

    if not actual_values.issubset(allowed_values):
        raise ValueError(f"Unexpected target values found in Churn: {sorted(actual_values)}")


def print_validation_summary(df: pd.DataFrame) -> None:
    total_rows = len(df)
    churn_rate = float((df["Churn"] == "Yes").mean())
    total_charges_missing = int(df["TotalCharges"].isna().sum())

    print("Validation summary")
    print(f"rows={total_rows}")
    print(f"columns={len(df.columns)}")
    print(f"churn_rate={churn_rate:.4f}")
    print(f"tenure_min={int(df['tenure'].min())}")
    print(f"tenure_max={int(df['tenure'].max())}")
    print(f"monthly_charges_min={float(df['MonthlyCharges'].min()):.2f}")
    print(f"monthly_charges_max={float(df['MonthlyCharges'].max()):.2f}")
    print(f"total_charges_missing_after_cleaning={total_charges_missing}")


def main() -> None:
    raw_df = load_raw_dataset(settings.raw_data_path)
    validate_schema(raw_df)

    cleaned_df = clean_total_charges(raw_df)
    validate_row_count(cleaned_df)
    validate_duplicates(cleaned_df)
    validate_missing_values(cleaned_df)
    validate_business_ranges(cleaned_df)
    validate_target_values(cleaned_df)
    print_validation_summary(cleaned_df)


if __name__ == "__main__":
    main()
