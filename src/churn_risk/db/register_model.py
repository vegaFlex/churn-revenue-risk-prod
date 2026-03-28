from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from churn_risk.config import settings
from churn_risk.db.base import engine


def load_metrics() -> dict:
    metrics_path = Path(settings.train_metrics_path)
    if not metrics_path.exists():
        raise FileNotFoundError(f"Training metrics file not found: {metrics_path}")

    return json.loads(metrics_path.read_text(encoding="utf-8"))


def build_registry_payload(metrics: dict) -> pd.DataFrame:
    selected_model_name = metrics["selected_model"]["name"]
    selected_model_metrics = metrics[selected_model_name]
    version = datetime.now(UTC).strftime("v%Y%m%d_%H%M%S")

    return pd.DataFrame(
        [
            {
                "model_version": version,
                "model_name": "customer_churn_revenue_risk",
                "model_type": selected_model_name,
                "auc_score": float(selected_model_metrics["auc"]),
                "precision_score": float(selected_model_metrics["precision"]),
                "recall_score": float(selected_model_metrics["recall"]),
                "f1_score": float(selected_model_metrics["f1"]),
                "artifact_path": settings.model_path,
                "preprocessor_path": settings.preprocessor_path,
                "registered_at": datetime.now(UTC),
            }
        ]
    )


def main() -> None:
    metrics = load_metrics()
    payload = build_registry_payload(metrics)
    payload.to_sql("model_registry", engine, if_exists="append", index=False)
    print(
        "Registered model version "
        f"{payload.iloc[0]['model_version']} "
        f"using {payload.iloc[0]['model_type']}"
    )


if __name__ == "__main__":
    main()
