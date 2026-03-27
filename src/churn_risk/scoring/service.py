from __future__ import annotations

from datetime import UTC, datetime

import joblib
import pandas as pd

from churn_risk.train.train_model import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS


def load_inference_artifacts(model_path: str, preprocessor_path: str):
    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    return model, preprocessor


def build_model_input(df: pd.DataFrame) -> pd.DataFrame:
    model_columns = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS
    return df[model_columns].copy()


def predict_churn_probabilities(df: pd.DataFrame, model, preprocessor) -> pd.Series:
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


def build_score_output(df: pd.DataFrame, churn_probabilities: pd.Series) -> pd.DataFrame:
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
    return scores
