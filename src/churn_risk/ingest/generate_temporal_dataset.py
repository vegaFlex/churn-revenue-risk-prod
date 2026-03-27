from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from churn_risk.config import settings
from churn_risk.scoring.service import estimate_expected_months_remaining


def load_scores_dataset(path: str) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Scores dataset not found: {source}")

    return pd.read_parquet(source)


def month_end_series(anchor_date: pd.Timestamp, periods: int) -> list[pd.Timestamp]:
    return [
        (anchor_date - pd.DateOffset(months=months_back)).to_period("M").to_timestamp("M")
        for months_back in range(periods - 1, -1, -1)
    ]


def deterministic_noise(size: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=0.03, size=size)


def build_customer_snapshots(base_df: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
    snapshot_frames: list[pd.DataFrame] = []
    anchor_date = pd.Timestamp(datetime.now(UTC).date())
    snapshot_dates = month_end_series(anchor_date=anchor_date, periods=periods)

    for months_back, snapshot_date in zip(range(periods - 1, -1, -1), snapshot_dates):
        frame = base_df.copy()
        frame["months_back"] = months_back
        frame["snapshot_date"] = snapshot_date
        frame["tenure_at_snapshot"] = (frame["tenure"] - months_back).clip(lower=0)
        frame = frame[frame["tenure_at_snapshot"] > 0].copy()

        if frame.empty:
            continue

        noise = deterministic_noise(size=len(frame), seed=months_back + 42)
        seasonality = 1 + noise

        probability_shift = (
            frame["months_back"] * 0.015
            + (frame["risk_segment"] == "high").astype(float) * 0.01
        )

        frame["monthly_revenue"] = (frame["MonthlyCharges"] * seasonality).round(2).clip(lower=18.0)
        frame["churn_probability"] = (frame["churn_probability"] - probability_shift).clip(0.01, 0.99)
        expected_months_input = frame[["Contract", "tenure_at_snapshot"]].rename(
            columns={"tenure_at_snapshot": "tenure"}
        )
        frame["expected_months_remaining"] = estimate_expected_months_remaining(
            expected_months_input
        )
        frame["revenue_at_risk"] = (
            frame["churn_probability"]
            * frame["monthly_revenue"]
            * frame["expected_months_remaining"]
        ).round(2)
        frame["risk_segment"] = pd.cut(
            frame["churn_probability"],
            bins=[-0.01, 0.3, 0.7, 1.0],
            labels=["low", "medium", "high"],
        ).astype(str)
        frame["observed_churn_event"] = (
            (frame["churn_flag"] == 1) & (frame["months_back"] == 0)
        ).astype("int64")
        frame["active_customer_flag"] = 1

        selected_columns = [
            "snapshot_date",
            "customerID",
            "gender",
            "SeniorCitizen",
            "Partner",
            "Dependents",
            "Contract",
            "PaymentMethod",
            "InternetService",
            "tenure_at_snapshot",
            "monthly_revenue",
            "churn_probability",
            "expected_months_remaining",
            "revenue_at_risk",
            "risk_segment",
            "observed_churn_event",
            "active_customer_flag",
        ]
        snapshot_frames.append(frame[selected_columns].copy())

    if not snapshot_frames:
        raise RuntimeError("No temporal snapshots were generated.")

    return pd.concat(snapshot_frames, ignore_index=True)


def save_snapshots(df: pd.DataFrame, output_path: str) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destination, index=False)
    print(f"Saved customer snapshots to {destination}")


def main() -> None:
    scores_df = load_scores_dataset(settings.scores_path)
    snapshots_df = build_customer_snapshots(scores_df)
    save_snapshots(snapshots_df, settings.customer_snapshots_path)


if __name__ == "__main__":
    main()
