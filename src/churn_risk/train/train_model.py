from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from churn_risk.config import settings


RANDOM_STATE = 42
TARGET_COLUMN = "churn_flag"
ID_COLUMNS = ["customerID"]
CATEGORICAL_COLUMNS = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "tenure_bucket",
]
NUMERIC_COLUMNS = [
    "SeniorCitizen",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "contract_term_months",
    "monthly_charges_log",
    "has_internet",
    "has_security",
    "payment_risk_flag",
    "is_senior",
    "has_partner",
    "has_dependents",
]


def load_feature_dataset(path: str) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Feature dataset not found: {source}")

    return pd.read_parquet(source)


def build_training_matrices(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_columns = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS
    x = df[feature_columns].copy()
    y = df[TARGET_COLUMN].copy()
    return x, y


def split_dataset(
    x: pd.DataFrame, y: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_COLUMNS),
            ("categorical", categorical_pipeline, CATEGORICAL_COLUMNS),
        ]
    )


def train_models(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> tuple[Pipeline, dict[str, dict[str, float]]]:
    model_candidates = {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=400,
            max_depth=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    metrics_summary: dict[str, dict[str, float]] = {}
    best_model_name = ""
    best_auc = -1.0
    best_pipeline: Pipeline | None = None

    for model_name, estimator in model_candidates.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("model", estimator),
            ]
        )
        pipeline.fit(x_train, y_train)

        probabilities = pipeline.predict_proba(x_test)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)

        model_metrics = {
            "auc": float(roc_auc_score(y_test, probabilities)),
            "precision": float(precision_score(y_test, predictions, zero_division=0)),
            "recall": float(recall_score(y_test, predictions, zero_division=0)),
            "f1": float(f1_score(y_test, predictions, zero_division=0)),
        }
        metrics_summary[model_name] = model_metrics

        if model_metrics["auc"] > best_auc:
            best_auc = model_metrics["auc"]
            best_model_name = model_name
            best_pipeline = pipeline

    if best_pipeline is None:
        raise RuntimeError("No model was trained successfully.")

    metrics_summary["selected_model"] = {"name": best_model_name, "auc": best_auc}
    return best_pipeline, metrics_summary


def save_artifacts(trained_pipeline: Pipeline, metrics_summary: dict[str, dict[str, float]]) -> None:
    model_destination = Path(settings.model_path)
    preprocessor_destination = Path(settings.preprocessor_path)
    metrics_destination = Path(settings.train_metrics_path)

    model_destination.parent.mkdir(parents=True, exist_ok=True)
    preprocessor_destination.parent.mkdir(parents=True, exist_ok=True)
    metrics_destination.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(trained_pipeline.named_steps["model"], model_destination)
    joblib.dump(trained_pipeline.named_steps["preprocessor"], preprocessor_destination)
    metrics_destination.write_text(json.dumps(metrics_summary, indent=2), encoding="utf-8")

    print(f"Saved model artifact to {model_destination}")
    print(f"Saved preprocessor artifact to {preprocessor_destination}")
    print(f"Saved metrics report to {metrics_destination}")


def train_and_save() -> dict[str, dict[str, float]]:
    df = load_feature_dataset(settings.features_path)
    x, y = build_training_matrices(df)
    x_train, x_test, y_train, y_test = split_dataset(x, y)
    trained_pipeline, metrics_summary = train_models(x_train, x_test, y_train, y_test)
    save_artifacts(trained_pipeline, metrics_summary)
    return metrics_summary


def main() -> None:
    train_and_save()


if __name__ == "__main__":
    main()
