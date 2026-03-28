# Revenue Risk and Customer Churn Intelligence Platform - User Guide

## 1. Purpose of the Application

Revenue Risk and Customer Churn Intelligence Platform is a browser-based risk intelligence application for identifying customers with elevated churn likelihood and prioritising revenue retention actions.

The application combines:
- churn probability scoring
- revenue-at-risk estimation
- segment-based risk review
- browser dashboard analytics
- monitoring and alert visibility
- compatible dataset upload preview
- realtime API testing

This guide explains what each part of the application does and how to use it during risk review.

## 2. Who the App Is For

The application is designed for:
- customer retention analysts
- revenue operations teams
- BI and analytics reviewers
- product managers reviewing churn pressure
- technical reviewers validating API and monitoring workflows

## 3. Main Navigation

### Overview
Main business dashboard.

Use it for:
- monitoring current revenue at risk
- reviewing churn pressure
- checking the trend trajectory
- identifying the highest-priority risky customers

### Customers
Analyst-facing queue for reviewing scored customers.

Use it for:
- filtering by risk segment
- filtering by contract type
- prioritising who should be worked first

### Monitoring
Operational monitoring page.

Use it for:
- reviewing data drift
- reviewing prediction drift
- checking threshold alerts
- confirming whether the current model behaviour looks stable

### Upload
Compatible dataset scoring preview.

Use it for:
- uploading CSV, Parquet, or Excel files
- validating schema compatibility
- generating in-memory churn and revenue-risk previews

### API Docs
Swagger documentation for the realtime API.

Use it for:
- testing `POST /score`
- reviewing payload and response contracts
- demonstrating the technical integration layer

## 4. Dashboard

URL:
`/`

The dashboard is the main business-facing screen.

### What the dashboard shows

#### KPI cards
Main current-state indicators:
- Total Revenue At Risk
- Average Churn Probability
- High Risk Customers
- Customers Scored

#### Trend Monitor
Shows the synthetic 12-month trajectory for:
- average churn pressure
- total revenue exposure
- directional risk change over time

#### Current Risk Mix
Summarises how many customers are currently in:
- high risk
- medium risk
- low risk

#### Top Risky Customers
Highlights the customers with the highest current projected revenue exposure.

Use it to identify:
- who should be prioritised first
- which contract/payment combinations are most exposed

## 5. Customer Explorer

URL:
`/customers`

This page is the main analyst queue.

### What it does
- shows the latest scored customers
- sorts by `revenue_at_risk` and `churn_probability`
- supports filtering by:
  - risk segment
  - contract type

### What you can review
- customer ID
- contract type
- payment method
- monthly charges
- churn probability
- expected months remaining
- revenue at risk
- risk segment

Use it when the dashboard shortlist is not enough and you need a wider review queue.

## 6. Monitoring Center

URL:
`/monitoring`

This page is the main model-operations view.

### What it shows

#### Alert Queue
Shows the metrics that currently breached configured thresholds.

Examples:
- `tenure_mean_delta`
- `avg_churn_probability_delta`
- `high_risk_share_delta`

#### Metric Ledger
Shows the latest recorded monitoring rows from `drift_metrics`.

Use it to:
- review the current drift state
- explain alerts during demos or technical review
- confirm whether recent behaviour changes are acceptable

## 7. Dataset Upload Preview

URL:
`/upload`

### Purpose
Allows users to test compatible customer files without replacing the core production snapshot.

### Supported formats
- CSV
- Parquet
- Excel (`.xlsx`)

### What happens during upload
1. The file is read in memory
2. Required columns are validated
3. Features are generated
4. The trained model scores the uploaded rows
5. KPI summary and top uploaded customers are shown in the browser

### What this page does not do
- it does not automatically overwrite the main production scoring snapshot
- it does not yet persist uploaded runs into history tables

## 8. Realtime API

Key endpoints:
- `GET /health`
- `POST /score`
- `GET /docs`

Use the API layer for:
- direct technical demos
- integration testing
- validating one customer profile at a time

## 9. Typical User Flows

### Business review flow
1. Open `Overview`
2. Review KPI cards
3. Review the trend monitor
4. Check the current risk mix
5. Open top risky customers

### Analyst prioritisation flow
1. Open `Customers`
2. Filter by `high` risk
3. Review revenue-at-risk ordering
4. Focus on month-to-month or electronic-check customers first

### Monitoring review flow
1. Open `Monitoring`
2. Check the alert queue
3. Review the latest metric ledger
4. Confirm whether drift behaviour looks acceptable

### Compatible dataset review flow
1. Open `Upload`
2. Select a compatible input file
3. Run scoring preview
4. Review KPI summary and top exposed customers

## 10. Troubleshooting

### The app does not open on `8000`
The project may already have another service on that port. Use:
`uvicorn churn_risk.api.app:app --host 127.0.0.1 --port 8010 --reload`

### The upload page shows a schema error
Check:
- required columns
- column spelling
- numeric charge fields
- compatible contract and service values

### Monitoring looks empty
Run the monitoring jobs first:
- `python -m churn_risk.monitoring.data_drift`
- `python -m churn_risk.monitoring.prediction_drift`
- `python -m churn_risk.monitoring.threshold_alerts`

### Uploaded files score differently from the main dataset
That can be expected if the uploaded population has a different customer mix from the base telco-compatible dataset.
