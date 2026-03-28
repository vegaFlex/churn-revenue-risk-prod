from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from churn_risk.db.base import engine


def load_latest_model_registry() -> pd.DataFrame:
    query = text(
        """
        SELECT
            model_version,
            model_name,
            model_type,
            auc_score,
            precision_score,
            recall_score,
            f1_score,
            artifact_path,
            preprocessor_path,
            registered_at
        FROM model_registry
        ORDER BY registered_at DESC
        LIMIT 5
        """
    )
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    if not df.empty:
        df["registered_at"] = pd.to_datetime(df["registered_at"])
    return df


def load_latest_monitoring_snapshot() -> pd.DataFrame:
    query = text(
        """
        SELECT
            snapshot_date,
            metric_scope,
            metric_name,
            metric_value,
            threshold_value,
            status,
            created_at
        FROM drift_metrics
        ORDER BY snapshot_date DESC, created_at DESC
        """
    )
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    if not df.empty:
        df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def build_admin_context() -> dict:
    registry_df = load_latest_model_registry()
    monitoring_df = load_latest_monitoring_snapshot()

    latest_registry_rows = registry_df.to_dict(orient="records")
    for row in latest_registry_rows:
        row["registered_at_display"] = pd.to_datetime(row["registered_at"]).strftime("%Y-%m-%d %H:%M")
        row["auc_display"] = f"{float(row['auc_score']):.4f}"
        row["precision_display"] = f"{float(row['precision_score']):.4f}"
        row["recall_display"] = f"{float(row['recall_score']):.4f}"
        row["f1_display"] = f"{float(row['f1_score']):.4f}"

    latest_snapshot_date = None
    monitoring_summary = {
        "alerts": 0,
        "metrics": 0,
        "snapshot": "No monitoring data",
    }
    if not monitoring_df.empty:
        latest_snapshot_date = monitoring_df["snapshot_date"].max()
        latest_metrics = monitoring_df[monitoring_df["snapshot_date"] == latest_snapshot_date].copy()
        monitoring_summary = {
            "alerts": int((latest_metrics["status"] == "alert").sum()),
            "metrics": int(len(latest_metrics)),
            "snapshot": latest_snapshot_date.strftime("%Y-%m-%d"),
        }

    control_cards = [
        {
            "label": "Access Policy",
            "value": "Admin only",
            "hint": "Upload execution, retraining workflows, and future controls stay restricted.",
        },
        {
            "label": "Latest Monitoring Snapshot",
            "value": monitoring_summary["snapshot"],
            "hint": f"{monitoring_summary['metrics']} metrics recorded in the latest monitoring run.",
        },
        {
            "label": "Active Alerts",
            "value": str(monitoring_summary["alerts"]),
            "hint": "Alerts currently visible in the latest monitoring snapshot.",
        },
        {
            "label": "Registered Models",
            "value": str(len(latest_registry_rows)),
            "hint": "Most recent model versions visible from the model registry table.",
        },
    ]

    allowed_actions = [
        "Review the latest registered model versions and their metrics.",
        "Inspect monitoring readiness before retraining or release actions.",
        "Use this page as the internal control center for future admin-only operations.",
    ]

    planned_actions = [
        "Trigger retraining workflows from the browser.",
        "Register freshly trained models after validation.",
        "Run monitoring jobs and refresh alert state from a protected UI.",
    ]

    return {
        "page_title": "Admin Controls",
        "control_cards": control_cards,
        "registry_rows": latest_registry_rows,
        "allowed_actions": allowed_actions,
        "planned_actions": planned_actions,
    }
