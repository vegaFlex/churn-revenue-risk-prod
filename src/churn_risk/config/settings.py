from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    raw_data_url: str = os.getenv(
        "RAW_DATA_URL",
        "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv",
    )
    raw_data_path: str = os.getenv("RAW_DATA_PATH", "data/raw/telco_churn.csv")
    parquet_raw_path: str = os.getenv("PARQUET_RAW_PATH", "data/raw/telco_churn.parquet")
    features_path: str = os.getenv("FEATURES_PATH", "data/processed/features.parquet")
    scores_path: str = os.getenv("SCORES_PATH", "data/processed/scores.parquet")
    customer_snapshots_path: str = os.getenv(
        "CUSTOMER_SNAPSHOTS_PATH",
        "data/processed/customer_snapshots.parquet",
    )
    model_path: str = os.getenv("MODEL_PATH", "artifacts/model.joblib")
    preprocessor_path: str = os.getenv("PREPROCESSOR_PATH", "artifacts/preprocessor.joblib")
    train_metrics_path: str = os.getenv("TRAIN_METRICS_PATH", "reports/train_metrics.json")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:CHANGE_ME@localhost:5432/churn_risk",
    )
    session_secret_key: str = os.getenv("SESSION_SECRET_KEY", "CHANGE_ME_SESSION_SECRET")
    admin_username: str = os.getenv("ADMIN_USERNAME", "")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "")
    alert_revenue_at_risk_total: float = float(os.getenv("ALERT_REVENUE_AT_RISK_TOTAL", "50000"))
    alert_avg_churn_probability: float = float(os.getenv("ALERT_AVG_CHURN_PROBABILITY", "0.45"))


settings = Settings()
