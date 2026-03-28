from __future__ import annotations

import json
import re
from io import BytesIO, StringIO
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd

from churn_risk.features.build_features import (
    impute_total_charges,
    normalize_string_columns,
)
from churn_risk.scoring import (
    build_model_input,
    build_score_output,
    predict_churn_probabilities,
)


SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".xlsx"}
UPLOAD_STAGING_DIR = Path("data/processed/upload_staging")

REQUIRED_UPLOAD_COLUMNS = [
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
]

FIELD_SYNONYMS = {
    "customerID": ["customerid", "customer_id", "clientid", "client_id", "subscriberid", "subscriber_id"],
    "gender": ["gender", "sex"],
    "SeniorCitizen": ["seniorcitizen", "senior_citizen", "is_senior", "seniorflag", "senior_flag"],
    "Partner": ["partner", "has_partner", "partnerflag", "partner_flag"],
    "Dependents": ["dependents", "has_dependents", "dependentflag", "dependent_flag"],
    "tenure": ["tenure", "customer_tenure", "months_active", "months_with_company"],
    "PhoneService": ["phoneservice", "phone_service", "has_phone_service"],
    "MultipleLines": ["multiplelines", "multiple_lines", "multi_line", "multiline"],
    "InternetService": ["internetservice", "internet_service", "internet_type"],
    "OnlineSecurity": ["onlinesecurity", "online_security", "security_service"],
    "OnlineBackup": ["onlinebackup", "online_backup", "backup_service"],
    "DeviceProtection": ["deviceprotection", "device_protection", "protection_service"],
    "TechSupport": ["techsupport", "tech_support", "support_service"],
    "StreamingTV": ["streamingtv", "streaming_tv"],
    "StreamingMovies": ["streamingmovies", "streaming_movies"],
    "Contract": ["contract", "contract_type", "subscription_contract"],
    "PaperlessBilling": ["paperlessbilling", "paperless_billing", "paperless_flag"],
    "PaymentMethod": ["paymentmethod", "payment_method", "billing_method", "payment_type"],
    "MonthlyCharges": ["monthlycharges", "monthly_charges", "monthly_fee", "monthly_revenue", "monthly_amount"],
    "TotalCharges": ["totalcharges", "total_charges", "lifetime_value", "total_billed", "total_amount"],
}


def get_extension(filename: str) -> str:
    lowered = filename.lower()
    for extension in SUPPORTED_EXTENSIONS:
        if lowered.endswith(extension):
            return extension
    raise ValueError("Unsupported file type. Use CSV, Parquet, or Excel (.xlsx).")


def read_uploaded_dataset(filename: str, content: bytes) -> pd.DataFrame:
    extension = get_extension(filename)

    if extension == ".csv":
        return pd.read_csv(StringIO(content.decode("utf-8")))
    if extension == ".parquet":
        return pd.read_parquet(BytesIO(content))
    if extension == ".xlsx":
        return pd.read_excel(BytesIO(content))

    raise ValueError("Unsupported file type.")


def normalize_column_name(column_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", column_name.lower())


def save_uploaded_dataset(df: pd.DataFrame, original_filename: str) -> str:
    UPLOAD_STAGING_DIR.mkdir(parents=True, exist_ok=True)
    token = uuid4().hex
    df.to_parquet(UPLOAD_STAGING_DIR / f"{token}.parquet", index=False)
    metadata = {"original_filename": original_filename}
    (UPLOAD_STAGING_DIR / f"{token}.json").write_text(json.dumps(metadata), encoding="utf-8")
    return token


def load_staged_dataset(token: str) -> pd.DataFrame:
    dataset_path = UPLOAD_STAGING_DIR / f"{token}.parquet"
    if not dataset_path.exists():
        raise FileNotFoundError("Uploaded dataset staging file not found.")
    return pd.read_parquet(dataset_path)


def get_staged_metadata(token: str) -> dict:
    metadata_path = UPLOAD_STAGING_DIR / f"{token}.json"
    if not metadata_path.exists():
        return {}
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def suggest_schema_mapping(columns: list[str]) -> dict[str, str]:
    normalized_lookup = {normalize_column_name(column): column for column in columns}
    suggestions: dict[str, str] = {}

    for required_field in REQUIRED_UPLOAD_COLUMNS:
        for synonym in FIELD_SYNONYMS.get(required_field, []):
            normalized_synonym = normalize_column_name(synonym)
            if normalized_synonym in normalized_lookup:
                suggestions[required_field] = normalized_lookup[normalized_synonym]
                break
    return suggestions


def build_dataset_profile(df: pd.DataFrame) -> dict:
    rows = len(df)
    columns = len(df.columns)
    missing_total = int(df.isna().sum().sum())
    numeric_columns = int(len(df.select_dtypes(include=["number"]).columns))
    duplicate_rows = int(df.duplicated().sum())

    column_profiles = []
    for column in df.columns[:25]:
        series = df[column]
        sample_values = [str(value) for value in series.dropna().astype(str).head(3).tolist()]
        column_profiles.append(
            {
                "name": column,
                "dtype": str(series.dtype),
                "missing_pct": round(float(series.isna().mean() * 100), 1),
                "unique_values": int(series.nunique(dropna=True)),
                "sample_values": sample_values,
            }
        )

    suggestions = suggest_schema_mapping(df.columns.tolist())
    mapped_fields = len(suggestions)

    return {
        "rows": rows,
        "columns": columns,
        "missing_total": missing_total,
        "numeric_columns": numeric_columns,
        "duplicate_rows": duplicate_rows,
        "mapped_fields": mapped_fields,
        "required_fields": len(REQUIRED_UPLOAD_COLUMNS),
        "column_profiles": column_profiles,
        "mapping_suggestions": suggestions,
    }


def build_mapping_options(df: pd.DataFrame, suggestions: dict[str, str]) -> list[dict]:
    available_columns = df.columns.tolist()
    options = [{"value": "", "label": "-- not mapped --"}] + [
        {"value": column, "label": column} for column in available_columns
    ]

    return [
        {
            "required_field": field,
            "selected_value": suggestions.get(field, ""),
            "options": options,
        }
        for field in REQUIRED_UPLOAD_COLUMNS
    ]


def apply_column_mapping(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    selected_mapping = {
        source_column: target_field
        for target_field, source_column in mapping.items()
        if source_column and source_column in df.columns
    }

    return df.rename(columns=selected_mapping).copy()


def validate_upload_schema(df: pd.DataFrame) -> None:
    missing_fields = [field for field in REQUIRED_UPLOAD_COLUMNS if field not in df.columns]
    if missing_fields:
        raise ValueError(f"Missing required mapped fields: {missing_fields}")


def prepare_uploaded_features(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    validate_upload_schema(prepared)
    prepared["SeniorCitizen"] = pd.to_numeric(prepared["SeniorCitizen"], errors="coerce").fillna(0).astype("int64")
    prepared["tenure"] = pd.to_numeric(prepared["tenure"], errors="coerce").fillna(0).astype("int64")
    prepared["MonthlyCharges"] = pd.to_numeric(prepared["MonthlyCharges"], errors="coerce").fillna(0.0)
    prepared["TotalCharges"] = pd.to_numeric(prepared["TotalCharges"], errors="coerce")
    prepared = normalize_string_columns(prepared)
    prepared = impute_total_charges(prepared)
    prepared["tenure_bucket"] = pd.cut(
        prepared["tenure"],
        bins=[-1, 12, 24, 48, 72],
        labels=["0_12", "13_24", "25_48", "49_72"],
    ).astype(str)
    prepared["contract_term_months"] = prepared["Contract"].map(
        {
            "Month-to-month": 1,
            "One year": 12,
            "Two year": 24,
        }
    ).fillna(1).astype("int64")
    prepared["monthly_charges_log"] = np.log1p(prepared["MonthlyCharges"].clip(lower=0))
    prepared["has_internet"] = (prepared["InternetService"] != "No").astype("int64")
    prepared["has_security"] = (prepared["OnlineSecurity"] == "Yes").astype("int64")
    prepared["payment_risk_flag"] = (prepared["PaymentMethod"] == "Electronic check").astype("int64")
    prepared["is_senior"] = prepared["SeniorCitizen"].astype("int64")
    prepared["has_partner"] = (prepared["Partner"] == "Yes").astype("int64")
    prepared["has_dependents"] = (prepared["Dependents"] == "Yes").astype("int64")
    return prepared


def score_uploaded_dataset(df: pd.DataFrame, model, preprocessor) -> tuple[dict, list[dict]]:
    prepared = prepare_uploaded_features(df)
    model_input = build_model_input(prepared)
    churn_probabilities = predict_churn_probabilities(model_input, model, preprocessor)
    scored = build_score_output(prepared, churn_probabilities)

    summary = {
        "rows_scored": int(len(scored)),
        "total_revenue_at_risk": f"${float(scored['revenue_at_risk'].sum()):,.2f}",
        "avg_churn_probability": f"{float(scored['churn_probability'].mean()):.1%}",
        "high_risk_customers": int((scored["risk_segment"] == "high").sum()),
    }

    preview_rows = scored.sort_values("revenue_at_risk", ascending=False).head(15)[
        [
            "customerID",
            "Contract",
            "PaymentMethod",
            "MonthlyCharges",
            "churn_probability",
            "revenue_at_risk",
            "risk_segment",
        ]
    ].to_dict(orient="records")

    return summary, preview_rows
