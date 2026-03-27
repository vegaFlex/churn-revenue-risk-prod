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


def load_snapshots() -> pd.DataFrame:
    path = Path(settings.customer_snapshots_path)
    if not path.exists():
        raise FileNotFoundError(f"Customer snapshots dataset not found: {path}")

    df = pd.read_parquet(path).copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    return df


def build_dashboard_context() -> dict:
    scores_df = load_scores()
    snapshots_df = load_snapshots()

    latest_snapshot_date = scores_df["snapshot_date"].max()
    latest_scores = scores_df[scores_df["snapshot_date"] == latest_snapshot_date].copy()

    total_revenue_at_risk = float(latest_scores["revenue_at_risk"].sum())
    avg_churn_probability = float(latest_scores["churn_probability"].mean())
    high_risk_customers = int((latest_scores["risk_segment"] == "high").sum())
    customers_scored = int(len(latest_scores))

    risk_segment_counts = (
        latest_scores["risk_segment"].value_counts().reindex(["high", "medium", "low"], fill_value=0)
    )
    risk_segment_cards = [
        {"label": "High Risk", "value": int(risk_segment_counts["high"]), "tone": "high"},
        {"label": "Medium Risk", "value": int(risk_segment_counts["medium"]), "tone": "medium"},
        {"label": "Low Risk", "value": int(risk_segment_counts["low"]), "tone": "low"},
    ]

    top_risky_customers = (
        latest_scores.sort_values("revenue_at_risk", ascending=False)
        .head(12)[
            [
                "customerID",
                "Contract",
                "MonthlyCharges",
                "churn_probability",
                "revenue_at_risk",
                "risk_segment",
            ]
        ]
        .to_dict(orient="records")
    )

    trend_df = (
        snapshots_df.groupby("snapshot_date", as_index=False)
        .agg(
            avg_churn_probability=("churn_probability", "mean"),
            total_revenue_at_risk=("revenue_at_risk", "sum"),
            high_risk_share=("risk_segment", lambda s: float((s == "high").mean())),
        )
        .sort_values("snapshot_date")
    )
    trend_points = [
        {
            "snapshot_date": row["snapshot_date"].strftime("%Y-%m-%d"),
            "avg_churn_probability": round(float(row["avg_churn_probability"]), 4),
            "total_revenue_at_risk": round(float(row["total_revenue_at_risk"]), 2),
            "high_risk_share": round(float(row["high_risk_share"]), 4),
        }
        for _, row in trend_df.iterrows()
    ]

    return {
        "page_title": "Revenue Risk Command Center",
        "latest_snapshot_date": latest_snapshot_date.strftime("%Y-%m-%d"),
        "kpis": [
            {
                "label": "Total Revenue At Risk",
                "value": f"${total_revenue_at_risk:,.0f}",
                "hint": "Current total projected revenue exposure",
            },
            {
                "label": "Average Churn Probability",
                "value": f"{avg_churn_probability:.1%}",
                "hint": "Mean churn likelihood across the latest customer base",
            },
            {
                "label": "High Risk Customers",
                "value": f"{high_risk_customers:,}",
                "hint": "Customers currently classified in the high-risk segment",
            },
            {
                "label": "Customers Scored",
                "value": f"{customers_scored:,}",
                "hint": "Total customers scored in the latest batch snapshot",
            },
        ],
        "risk_segment_cards": risk_segment_cards,
        "top_risky_customers": top_risky_customers,
        "trend_points": trend_points,
    }
