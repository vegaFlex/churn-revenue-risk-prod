from __future__ import annotations

from pathlib import Path

import pandas as pd

from churn_risk.config import settings
from churn_risk.scoring import (
    build_model_input,
    build_score_output,
    load_inference_artifacts,
    predict_churn_probabilities,
)


def load_features(path: str) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Feature dataset not found: {source}")

    return pd.read_parquet(source)


def build_batch_snapshot(df: pd.DataFrame, churn_probabilities: pd.Series) -> pd.DataFrame:
    scores = build_score_output(df, churn_probabilities)
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
    model, preprocessor = load_inference_artifacts(settings.model_path, settings.preprocessor_path)
    model_input = build_model_input(feature_df)
    churn_probabilities = predict_churn_probabilities(model_input, model, preprocessor)
    scores_df = build_batch_snapshot(feature_df, churn_probabilities)
    save_scores(scores_df, settings.scores_path)


if __name__ == "__main__":
    main()
