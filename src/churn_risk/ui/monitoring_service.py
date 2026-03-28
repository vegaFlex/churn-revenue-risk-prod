from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from churn_risk.db.base import engine


def load_monitoring_metrics() -> pd.DataFrame:
    query = text(
        """
        SELECT
            snapshot_date,
            metric_name,
            metric_scope,
            metric_value,
            threshold_value,
            status,
            details,
            created_at
        FROM drift_metrics
        ORDER BY snapshot_date DESC, metric_scope, metric_name
        """
    )
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    if df.empty:
        return df

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def build_monitoring_context() -> dict:
    metrics_df = load_monitoring_metrics()
    if metrics_df.empty:
        return {
            "page_title": "Monitoring Center",
            "latest_snapshot_date": "No data",
            "summary_cards": [],
            "alert_rows": [],
            "metric_rows": [],
        }

    latest_snapshot_date = metrics_df["snapshot_date"].max()
    latest_metrics = metrics_df[metrics_df["snapshot_date"] == latest_snapshot_date].copy()

    summary_cards = [
        {
            "label": "Active Alerts",
            "value": int((latest_metrics["status"] == "alert").sum()),
            "tone": "high" if (latest_metrics["status"] == "alert").sum() > 0 else "low",
        },
        {
            "label": "Data Drift Metrics",
            "value": int((latest_metrics["metric_scope"] == "data_drift").sum()),
            "tone": "medium",
        },
        {
            "label": "Prediction Drift Metrics",
            "value": int((latest_metrics["metric_scope"] == "prediction_drift").sum()),
            "tone": "medium",
        },
        {
            "label": "Threshold Checks",
            "value": int((latest_metrics["metric_scope"] == "threshold_alert").sum()),
            "tone": "low",
        },
    ]

    alert_rows = (
        latest_metrics[latest_metrics["status"] == "alert"]
        .sort_values(["metric_scope", "metric_name"])
        .to_dict(orient="records")
    )
    metric_rows = latest_metrics.sort_values(["metric_scope", "metric_name"]).to_dict(orient="records")

    for row in alert_rows + metric_rows:
        row["snapshot_date"] = pd.to_datetime(row["snapshot_date"]).strftime("%Y-%m-%d")
        row["metric_value_display"] = f"{float(row['metric_value']):,.4f}"
        row["threshold_value_display"] = (
            f"{float(row['threshold_value']):,.4f}" if row["threshold_value"] is not None else "-"
        )

    return {
        "page_title": "Monitoring Center",
        "latest_snapshot_date": latest_snapshot_date.strftime("%Y-%m-%d"),
        "summary_cards": summary_cards,
        "alert_rows": alert_rows,
        "metric_rows": metric_rows,
    }
