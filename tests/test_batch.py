from __future__ import annotations

import pandas as pd

from churn_risk.batch.score_batch import build_batch_snapshot, load_features
from churn_risk.config import settings
from churn_risk.scoring import build_model_input, load_inference_artifacts, predict_churn_probabilities


def test_batch_scoring_smoke() -> None:
    feature_df = load_features(settings.features_path).head(25).copy()
    model, preprocessor = load_inference_artifacts(settings.model_path, settings.preprocessor_path)
    model_input = build_model_input(feature_df)
    probabilities = predict_churn_probabilities(model_input, model, preprocessor)
    snapshot = build_batch_snapshot(feature_df, probabilities)

    assert len(snapshot) == 25
    assert set(
        [
            "customerID",
            "churn_probability",
            "revenue_at_risk",
            "risk_segment",
            "snapshot_date",
        ]
    ).issubset(snapshot.columns)
    assert snapshot["churn_probability"].between(0, 1).all()
    assert snapshot["revenue_at_risk"].ge(0).all()
    assert snapshot["risk_segment"].isin(["low", "medium", "high"]).all()
    assert pd.api.types.is_datetime64_any_dtype(snapshot["snapshot_date"])
