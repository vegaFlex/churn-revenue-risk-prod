from __future__ import annotations

from datetime import datetime

import pandas as pd

from churn_risk.db.base import engine


def save_metrics(metrics_df: pd.DataFrame) -> None:
    payload = metrics_df.copy()
    payload["snapshot_date"] = pd.to_datetime(payload["snapshot_date"]).dt.date
    payload["created_at"] = datetime.utcnow()
    payload.to_sql("drift_metrics", engine, if_exists="append", index=False)
    print(f"Saved {len(payload)} monitoring metrics to drift_metrics")
