from __future__ import annotations

from datetime import datetime

import pandas as pd

from churn_risk.config import settings
from churn_risk.monitoring.metrics_store import save_metrics


def load_scores() -> pd.DataFrame:
    return pd.read_parquet(settings.scores_path)


def build_threshold_alerts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    latest_date = df["snapshot_date"].max()
    latest = df[df["snapshot_date"] == latest_date].copy()

    total_revenue_at_risk = float(latest["revenue_at_risk"].sum())
    avg_churn_probability = float(latest["churn_probability"].mean())

    alerts = [
        {
            "snapshot_date": latest_date,
            "metric_name": "total_revenue_at_risk",
            "metric_scope": "threshold_alert",
            "metric_value": total_revenue_at_risk,
            "threshold_value": settings.alert_revenue_at_risk_total,
            "status": "alert"
            if total_revenue_at_risk > settings.alert_revenue_at_risk_total
            else "ok",
            "details": (
                f"snapshot_date={latest_date.date()}, "
                f"total_revenue_at_risk={total_revenue_at_risk:.2f}"
            ),
        },
        {
            "snapshot_date": latest_date,
            "metric_name": "avg_churn_probability",
            "metric_scope": "threshold_alert",
            "metric_value": avg_churn_probability,
            "threshold_value": settings.alert_avg_churn_probability,
            "status": "alert"
            if avg_churn_probability > settings.alert_avg_churn_probability
            else "ok",
            "details": (
                f"snapshot_date={latest_date.date()}, "
                f"avg_churn_probability={avg_churn_probability:.4f}"
            ),
        },
    ]
    return pd.DataFrame(alerts)


def main() -> None:
    scores_df = load_scores()
    alerts_df = build_threshold_alerts(scores_df)
    save_metrics(alerts_df)


if __name__ == "__main__":
    main()
