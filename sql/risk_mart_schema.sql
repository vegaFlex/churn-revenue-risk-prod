CREATE TABLE IF NOT EXISTS customers_raw (
    customer_id VARCHAR(32) PRIMARY KEY,
    gender VARCHAR(16),
    senior_citizen INTEGER,
    partner VARCHAR(8),
    dependents VARCHAR(8),
    tenure INTEGER,
    phone_service VARCHAR(32),
    multiple_lines VARCHAR(32),
    internet_service VARCHAR(32),
    online_security VARCHAR(32),
    online_backup VARCHAR(32),
    device_protection VARCHAR(32),
    tech_support VARCHAR(32),
    streaming_tv VARCHAR(32),
    streaming_movies VARCHAR(32),
    contract VARCHAR(32),
    paperless_billing VARCHAR(8),
    payment_method VARCHAR(64),
    monthly_charges DOUBLE PRECISION,
    total_charges DOUBLE PRECISION,
    churn_flag INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS features (
    customer_id VARCHAR(32) PRIMARY KEY,
    tenure_bucket VARCHAR(16),
    contract_term_months INTEGER,
    monthly_charges_log DOUBLE PRECISION,
    has_internet INTEGER,
    has_security INTEGER,
    payment_risk_flag INTEGER,
    is_senior INTEGER,
    has_partner INTEGER,
    has_dependents INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scores_daily (
    snapshot_date DATE,
    customer_id VARCHAR(32),
    gender VARCHAR(16),
    senior_citizen INTEGER,
    partner VARCHAR(8),
    dependents VARCHAR(8),
    tenure INTEGER,
    internet_service VARCHAR(32),
    contract VARCHAR(32),
    payment_method VARCHAR(64),
    monthly_charges DOUBLE PRECISION,
    total_charges DOUBLE PRECISION,
    churn_probability DOUBLE PRECISION,
    monthly_revenue DOUBLE PRECISION,
    expected_months_remaining DOUBLE PRECISION,
    revenue_at_risk DOUBLE PRECISION,
    risk_segment VARCHAR(16),
    churn_flag INTEGER,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (snapshot_date, customer_id)
);

CREATE TABLE IF NOT EXISTS customer_snapshots (
    snapshot_date DATE,
    customer_id VARCHAR(32),
    gender VARCHAR(16),
    senior_citizen INTEGER,
    partner VARCHAR(8),
    dependents VARCHAR(8),
    contract VARCHAR(32),
    payment_method VARCHAR(64),
    internet_service VARCHAR(32),
    tenure_at_snapshot INTEGER,
    monthly_revenue DOUBLE PRECISION,
    churn_probability DOUBLE PRECISION,
    expected_months_remaining DOUBLE PRECISION,
    revenue_at_risk DOUBLE PRECISION,
    risk_segment VARCHAR(16),
    observed_churn_event INTEGER,
    active_customer_flag INTEGER
);

CREATE TABLE IF NOT EXISTS drift_metrics (
    metric_id SERIAL PRIMARY KEY,
    snapshot_date DATE,
    metric_name VARCHAR(64),
    metric_scope VARCHAR(32),
    metric_value DOUBLE PRECISION,
    threshold_value DOUBLE PRECISION,
    status VARCHAR(16),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_registry (
    model_version VARCHAR(32) PRIMARY KEY,
    model_name VARCHAR(64),
    model_type VARCHAR(64),
    auc_score DOUBLE PRECISION,
    precision_score DOUBLE PRECISION,
    recall_score DOUBLE PRECISION,
    f1_score DOUBLE PRECISION,
    artifact_path VARCHAR(255),
    preprocessor_path VARCHAR(255),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
