from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd

from churn_risk.config import settings
from churn_risk.train.train_model import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS


def load_features(path: str) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Feature dataset not found: {source}")

    return pd.read_parquet(source)


def load_artifacts(model_path: str, preprocessor_path: str):
    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    return model, preprocessor


def build_model_input(df: pd.DataFrame) -> pd.DataFrame:
    model_columns = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS
    return df[model_columns].copy()


def score_probabilities(df: pd.DataFrame, model, preprocessor) -> pd.Series:
    transformed = preprocessor.transform(df)
    probabilities = model.predict_proba(transformed)[:, 1]
    return pd.Series(probabilities, index=df.index, name="churn_probability")


def estimate_expected_months_remaining(df: pd.DataFrame) -> pd.Series:
    contract_buffer = df["Contract"].map(
        {
            "Month-to-month": 3,
            "One year": 12,
            "Two year": 18,
        }
    ).fillna(6)

    tenure_adjustment = (df["tenure"] / 12).clip(lower=0, upper=6)
    expected_months = (contract_buffer - tenure_adjustment).clip(lower=1)
    return expected_months.round(2)


def assign_risk_segment(probabilities: pd.Series) -> pd.Series:
    return pd.cut(
        probabilities,
        bins=[-0.01, 0.3, 0.7, 1.0],
        labels=["low", "medium", "high"],
    ).astype(str)


def build_scores(df: pd.DataFrame, churn_probabilities: pd.Series) -> pd.DataFrame:
    scores = df.copy()
    scores["churn_probability"] = churn_probabilities
    scores["monthly_revenue"] = scores["MonthlyCharges"]
    scores["expected_months_remaining"] = estimate_expected_months_remaining(scores)
    scores["revenue_at_risk"] = (
        scores["churn_probability"]
        * scores["monthly_revenue"]
        * scores["expected_months_remaining"]
    ).round(2)
    scores["risk_segment"] = assign_risk_segment(scores["churn_probability"])
    scores["snapshot_date"] = pd.to_datetime(datetime.now(UTC).date())

    selected_columns = [
        "snapshot_date",
        "customerID",
        "gender",
        "SeniorCitizen",
        "Partner",
        "Dependents",
        "tenure",
        "InternetService",
        "Contract",
        "PaymentMethod",
        "MonthlyCharges",
        "TotalCharges",
        "churn_probability",
        "monthly_revenue",
        "expected_months_remaining",
        "revenue_at_risk",
        "risk_segment",
        "churn_flag",
    ]
    return scores[selected_columns].copy()


def save_scores(df: pd.DataFrame, output_path: str) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destination, index=False)
    print(f"Saved batch scores to {destination}")


def main() -> None:
    feature_df = load_features(settings.features_path)
    model, preprocessor = load_artifacts(settings.model_path, settings.preprocessor_path)
    model_input = build_model_input(feature_df)
    churn_probabilities = score_probabilities(model_input, model, preprocessor)
    scores_df = build_scores(feature_df, churn_probabilities)
    save_scores(scores_df, settings.scores_path)


if __name__ == "__main__":
    main()
