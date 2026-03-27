from __future__ import annotations

import pandas as pd

from churn_risk.config import settings
from churn_risk.monitoring.metrics_store import save_metrics


def load_snapshots() -> pd.DataFrame:
    return pd.read_parquet(settings.customer_snapshots_path)


def build_prediction_drift_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    snapshot_dates = sorted(df["snapshot_date"].unique())
    if len(snapshot_dates) < 2:
        raise ValueError("At least two snapshot dates are required for prediction drift monitoring.")

    latest_date = snapshot_dates[-1]
    previous_date = snapshot_dates[-2]

    latest = df[df["snapshot_date"] == latest_date].copy()
    previous = df[df["snapshot_date"] == previous_date].copy()

    avg_churn_latest = latest["churn_probability"].mean()
    avg_churn_previous = previous["churn_probability"].mean()
    high_risk_latest = (latest["risk_segment"] == "high").mean()
    high_risk_previous = (previous["risk_segment"] == "high").mean()

    metrics = [
        {
            "snapshot_date": latest_date,
            "metric_name": "avg_churn_probability_delta",
            "metric_scope": "prediction_drift",
            "metric_value": float(avg_churn_latest - avg_churn_previous),
            "threshold_value": 0.03,
            "status": "alert" if abs(avg_churn_latest - avg_churn_previous) > 0.03 else "ok",
            "details": f"latest={avg_churn_latest:.4f}, previous={avg_churn_previous:.4f}",
        },
        {
            "snapshot_date": latest_date,
            "metric_name": "high_risk_share_delta",
            "metric_scope": "prediction_drift",
            "metric_value": float(high_risk_latest - high_risk_previous),
            "threshold_value": 0.03,
            "status": "alert" if abs(high_risk_latest - high_risk_previous) > 0.03 else "ok",
            "details": f"latest={high_risk_latest:.4f}, previous={high_risk_previous:.4f}",
        },
    ]
    return pd.DataFrame(metrics)


def main() -> None:
    snapshots_df = load_snapshots()
    metrics_df = build_prediction_drift_metrics(snapshots_df)
    save_metrics(metrics_df)


if __name__ == "__main__":
    main()
