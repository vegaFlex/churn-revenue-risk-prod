from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from churn_risk.db.base import Base


class CustomerRaw(Base):
    __tablename__ = "customers_raw"

    customer_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    gender: Mapped[str] = mapped_column(String(16))
    senior_citizen: Mapped[int] = mapped_column(Integer)
    partner: Mapped[str] = mapped_column(String(8))
    dependents: Mapped[str] = mapped_column(String(8))
    tenure: Mapped[int] = mapped_column(Integer)
    phone_service: Mapped[str] = mapped_column(String(32))
    multiple_lines: Mapped[str] = mapped_column(String(32))
    internet_service: Mapped[str] = mapped_column(String(32))
    online_security: Mapped[str] = mapped_column(String(32))
    online_backup: Mapped[str] = mapped_column(String(32))
    device_protection: Mapped[str] = mapped_column(String(32))
    tech_support: Mapped[str] = mapped_column(String(32))
    streaming_tv: Mapped[str] = mapped_column(String(32))
    streaming_movies: Mapped[str] = mapped_column(String(32))
    contract: Mapped[str] = mapped_column(String(32))
    paperless_billing: Mapped[str] = mapped_column(String(8))
    payment_method: Mapped[str] = mapped_column(String(64))
    monthly_charges: Mapped[float] = mapped_column(Float)
    total_charges: Mapped[float | None] = mapped_column(Float, nullable=True)
    churn_flag: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FeatureRow(Base):
    __tablename__ = "features"

    customer_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    tenure_bucket: Mapped[str] = mapped_column(String(16))
    contract_term_months: Mapped[int] = mapped_column(Integer)
    monthly_charges_log: Mapped[float] = mapped_column(Float)
    has_internet: Mapped[int] = mapped_column(Integer)
    has_security: Mapped[int] = mapped_column(Integer)
    payment_risk_flag: Mapped[int] = mapped_column(Integer)
    is_senior: Mapped[int] = mapped_column(Integer)
    has_partner: Mapped[int] = mapped_column(Integer)
    has_dependents: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ScoreDaily(Base):
    __tablename__ = "scores_daily"

    snapshot_date: Mapped[date] = mapped_column(Date, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    gender: Mapped[str] = mapped_column(String(16))
    senior_citizen: Mapped[int] = mapped_column(Integer)
    partner: Mapped[str] = mapped_column(String(8))
    dependents: Mapped[str] = mapped_column(String(8))
    tenure: Mapped[int] = mapped_column(Integer)
    internet_service: Mapped[str] = mapped_column(String(32))
    contract: Mapped[str] = mapped_column(String(32))
    payment_method: Mapped[str] = mapped_column(String(64))
    monthly_charges: Mapped[float] = mapped_column(Float)
    total_charges: Mapped[float | None] = mapped_column(Float, nullable=True)
    churn_probability: Mapped[float] = mapped_column(Float)
    monthly_revenue: Mapped[float] = mapped_column(Float)
    expected_months_remaining: Mapped[float] = mapped_column(Float)
    revenue_at_risk: Mapped[float] = mapped_column(Float)
    risk_segment: Mapped[str] = mapped_column(String(16))
    churn_flag: Mapped[int] = mapped_column(Integer)
    loaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CustomerSnapshot(Base):
    __tablename__ = "customer_snapshots"

    snapshot_date: Mapped[date] = mapped_column(Date, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    gender: Mapped[str] = mapped_column(String(16))
    senior_citizen: Mapped[int] = mapped_column(Integer)
    partner: Mapped[str] = mapped_column(String(8))
    dependents: Mapped[str] = mapped_column(String(8))
    contract: Mapped[str] = mapped_column(String(32))
    payment_method: Mapped[str] = mapped_column(String(64))
    internet_service: Mapped[str] = mapped_column(String(32))
    tenure_at_snapshot: Mapped[int] = mapped_column(Integer)
    monthly_revenue: Mapped[float] = mapped_column(Float)
    churn_probability: Mapped[float] = mapped_column(Float)
    expected_months_remaining: Mapped[float] = mapped_column(Float)
    revenue_at_risk: Mapped[float] = mapped_column(Float)
    risk_segment: Mapped[str] = mapped_column(String(16))
    observed_churn_event: Mapped[int] = mapped_column(Integer)
    active_customer_flag: Mapped[int] = mapped_column(Integer)


class DriftMetric(Base):
    __tablename__ = "drift_metrics"

    metric_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_date: Mapped[date] = mapped_column(Date)
    metric_name: Mapped[str] = mapped_column(String(64))
    metric_scope: Mapped[str] = mapped_column(String(32))
    metric_value: Mapped[float] = mapped_column(Float)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    model_version: Mapped[str] = mapped_column(String(32), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(64))
    model_type: Mapped[str] = mapped_column(String(64))
    auc_score: Mapped[float] = mapped_column(Float)
    precision_score: Mapped[float] = mapped_column(Float)
    recall_score: Mapped[float] = mapped_column(Float)
    f1_score: Mapped[float] = mapped_column(Float)
    artifact_path: Mapped[str] = mapped_column(String(255))
    preprocessor_path: Mapped[str] = mapped_column(String(255))
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AppUser(Base):
    __tablename__ = "app_users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
