from __future__ import annotations

from churn_risk.train.train_model import train_and_save


def main() -> None:
    metrics_summary = train_and_save()
    selected_model = metrics_summary["selected_model"]["name"]
    selected_auc = metrics_summary["selected_model"]["auc"]
    print(f"Retraining completed. Selected model: {selected_model} (AUC={selected_auc:.4f})")


if __name__ == "__main__":
    main()
