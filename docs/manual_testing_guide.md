# Revenue Risk and Customer Churn Intelligence Platform - Manual Testing Guide

## 1. Purpose

This guide provides a practical manual testing checklist for the browser app, API, and compatible dataset upload flow.

## 2. Environment Preparation

Before testing:
- activate the virtual environment
- confirm PostgreSQL is available
- confirm `.env` is configured correctly
- run the scoring and monitoring pipelines

Recommended local command:
`uvicorn churn_risk.api.app:app --host 127.0.0.1 --port 8010 --reload`

## 3. Browser Smoke Test

Open and confirm all of the following pages return successfully:
- `/`
- `/monitoring`
- `/customers`
- `/upload`
- `/docs`

Expected result:
- all pages load without server errors
- navigation works
- pages remain English-only

## 4. Dashboard Test

Open `/`

Confirm:
- KPI cards are visible
- trend chart renders
- risk mix cards render
- top risky customers section shows customer rows

Expected result:
- `Total Revenue At Risk` is populated
- customer cards/tables are readable on desktop and mobile

## 5. Monitoring Page Test

Open `/monitoring`

Confirm:
- monitoring summary cards render
- alert queue renders
- metric ledger renders

Expected result:
- at least one alert is visible after monitoring jobs are run
- no layout overlap exists on desktop or mobile

## 6. Customer Explorer Test

Open `/customers`

Confirm:
- page loads
- filter pills work
- customer rows update when filters are used

Expected result:
- filtering by `high` risk reduces the list
- contract filtering changes the current view

## 7. Upload Flow Test

Open `/upload`

Test with a compatible file.

Confirm:
- file picker is English-only
- upload succeeds
- KPI summary appears
- preview rows render

Expected result:
- no browser crash
- no Python exception page
- preview shows `Rows Scored`, `Total Revenue At Risk`, and `High Risk Customers`

## 8. API Test

Open `/docs`

Test `POST /score` with a valid payload.

Expected result:
- status `200`
- response includes:
  - `customer_id`
  - `churn_probability`
  - `monthly_revenue`
  - `expected_months_remaining`
  - `revenue_at_risk`
  - `risk_segment`

## 9. Database Validation

Confirm the main tables contain rows:
- `customers_raw`
- `features`
- `scores_daily`
- `customer_snapshots`
- `drift_metrics`
- `model_registry`

Expected result:
- no critical table is empty after the full pipeline run

## 10. Regression Checklist

After UI changes, always re-check:
- dashboard layout
- mobile dashboard layout
- monitoring layout
- upload page language
- screenshot paths in README
- Swagger docs access

## 11. Pass Criteria

The release is manually acceptable when:
- browser pages load
- API scoring works
- upload preview works
- monitoring metrics exist
- UI remains readable on desktop and mobile
- English-only wording is preserved across the app
