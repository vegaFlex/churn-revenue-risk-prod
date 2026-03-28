from __future__ import annotations

from pathlib import Path

import pandas as pd

from churn_risk.config import settings


def load_scores() -> pd.DataFrame:
    path = Path(settings.scores_path)
    if not path.exists():
        raise FileNotFoundError(f"Scores dataset not found: {path}")

    df = pd.read_parquet(path).copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    return df


def build_customers_context(
    risk_segment: str | None = None,
    contract: str | None = None,
    limit: int = 50,
) -> dict:
    scores_df = load_scores()
    latest_snapshot_date = scores_df["snapshot_date"].max()
    latest_scores = scores_df[scores_df["snapshot_date"] == latest_snapshot_date].copy()

    if risk_segment:
        latest_scores = latest_scores[latest_scores["risk_segment"] == risk_segment].copy()

    if contract:
        latest_scores = latest_scores[latest_scores["Contract"] == contract].copy()

    latest_scores = latest_scores.sort_values(
        ["revenue_at_risk", "churn_probability"],
        ascending=[False, False],
    ).head(limit)

    customer_rows = latest_scores[
        [
            "customerID",
            "Contract",
            "PaymentMethod",
            "MonthlyCharges",
            "churn_probability",
            "expected_months_remaining",
            "revenue_at_risk",
            "risk_segment",
        ]
    ].to_dict(orient="records")

    available_segments = ["high", "medium", "low"]
    available_contracts = ["Month-to-month", "One year", "Two year"]

    return {
        "page_title": "Customer Risk Explorer",
        "latest_snapshot_date": latest_snapshot_date.strftime("%Y-%m-%d"),
        "selected_risk_segment": risk_segment or "",
        "selected_contract": contract or "",
        "available_segments": available_segments,
        "available_contracts": available_contracts,
        "customer_rows": customer_rows,
        "customer_count": len(customer_rows),
    }
