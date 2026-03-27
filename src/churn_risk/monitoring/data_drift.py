from __future__ import annotations

import pandas as pd

from churn_risk.config import settings
from churn_risk.monitoring.metrics_store import save_metrics


def load_snapshots() -> pd.DataFrame:
    return pd.read_parquet(settings.customer_snapshots_path)


def build_data_drift_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    snapshot_dates = sorted(df["snapshot_date"].unique())
    if len(snapshot_dates) < 2:
        raise ValueError("At least two snapshot dates are required for data drift monitoring.")

    latest_date = snapshot_dates[-1]
    previous_date = snapshot_dates[-2]

    latest = df[df["snapshot_date"] == latest_date].copy()
    previous = df[df["snapshot_date"] == previous_date].copy()

    metrics = [
        {
            "snapshot_date": latest_date,
            "metric_name": "monthly_revenue_mean_delta",
            "metric_scope": "data_drift",
            "metric_value": float(latest["monthly_revenue"].mean() - previous["monthly_revenue"].mean()),
            "threshold_value": 5.0,
            "status": "alert"
            if abs(latest["monthly_revenue"].mean() - previous["monthly_revenue"].mean()) > 5.0
            else "ok",
            "details": f"latest={latest['monthly_revenue'].mean():.4f}, previous={previous['monthly_revenue'].mean():.4f}",
        },
        {
            "snapshot_date": latest_date,
            "metric_name": "tenure_mean_delta",
            "metric_scope": "data_drift",
            "metric_value": float(latest["tenure_at_snapshot"].mean() - previous["tenure_at_snapshot"].mean()),
            "threshold_value": 1.0,
            "status": "alert"
            if abs(latest["tenure_at_snapshot"].mean() - previous["tenure_at_snapshot"].mean()) > 1.0
            else "ok",
            "details": f"latest={latest['tenure_at_snapshot'].mean():.4f}, previous={previous['tenure_at_snapshot'].mean():.4f}",
        },
        {
            "snapshot_date": latest_date,
            "metric_name": "contract_month_to_month_share_delta",
            "metric_scope": "data_drift",
            "metric_value": float(
                (latest["Contract"] == "Month-to-month").mean()
                - (previous["Contract"] == "Month-to-month").mean()
            ),
            "threshold_value": 0.05,
            "status": "alert"
            if abs(
                (latest["Contract"] == "Month-to-month").mean()
                - (previous["Contract"] == "Month-to-month").mean()
            )
            > 0.05
            else "ok",
            "details": (
                f"latest={(latest['Contract'] == 'Month-to-month').mean():.4f}, "
                f"previous={(previous['Contract'] == 'Month-to-month').mean():.4f}"
            ),
        },
    ]
    return pd.DataFrame(metrics)


def main() -> None:
    snapshots_df = load_snapshots()
    metrics_df = build_data_drift_metrics(snapshots_df)
    save_metrics(metrics_df)


if __name__ == "__main__":
    main()
