from __future__ import annotations

from pathlib import Path

import pandas as pd

from churn_risk.config import settings


def build_clean_raw_dataset(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0}).astype("int64")
    return df


def save_parquet(df: pd.DataFrame, output_path: str) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destination, index=False)
    print(f"Saved parquet dataset to {destination}")


def main() -> None:
    df = build_clean_raw_dataset(settings.raw_data_path)
    save_parquet(df=df, output_path=settings.parquet_raw_path)


if __name__ == "__main__":
    main()
