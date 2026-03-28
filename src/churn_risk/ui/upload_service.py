from __future__ import annotations

from io import BytesIO, StringIO

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


def validate_upload_schema(df: pd.DataFrame) -> None:
    missing_columns = [column for column in REQUIRED_UPLOAD_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def prepare_uploaded_features(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    validate_upload_schema(prepared)
    prepared["SeniorCitizen"] = pd.to_numeric(prepared["SeniorCitizen"], errors="coerce").fillna(0).astype("int64")
    prepared["tenure"] = pd.to_numeric(prepared["tenure"], errors="coerce").fillna(0).astype("int64")
    prepared["MonthlyCharges"] = pd.to_numeric(prepared["MonthlyCharges"], errors="coerce")
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
