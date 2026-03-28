# Revenue Risk and Customer Churn Intelligence Platform - Buyer Guide

## 1. What the Product Solves

Revenue Risk and Customer Churn Intelligence Platform helps teams identify which customers are most likely to churn and how much revenue is currently exposed if no action is taken.

It turns machine learning output into operational decision support by combining:
- churn scoring
- revenue-at-risk estimation
- segment prioritisation
- drift monitoring
- browser-based review workflows
- protected user access
- schema-mapped dataset upload analysis

## 2. Ideal Buyer / Team

The product is most relevant for:
- retention analytics teams
- subscription and SaaS operators
- telecom-style customer operations teams
- BI teams that need risk-ready tables for dashboards
- product leaders who want customer-risk visibility beyond a notebook

## 3. Core Business Capabilities

### Churn Intelligence
Scores each customer with a churn probability.

### Revenue Exposure
Calculates `revenue_at_risk` using:
- churn probability
- monthly revenue
- expected months remaining

### Risk Segmentation
Classifies customers into:
- low risk
- medium risk
- high risk

### Operational Monitoring
Tracks:
- data drift
- prediction drift
- threshold alerts

### Browser-Based Review
Provides:
- executive dashboard
- customer explorer
- monitoring center
- login and role-aware access
- schema-mapped dataset upload preview
- internal admin controls

## 4. Why This Is More Than a Demo

This project goes beyond a single model notebook because it includes:
- reproducible ingestion and validation
- saved training artifacts
- batch scoring
- realtime API scoring
- PostgreSQL analytics tables
- temporal snapshot generation
- monitoring and alert pipelines
- browser-facing operational review pages

## 5. Differentiators

Compared with typical churn demo projects, this platform stands out because it:
- ties predictions directly to `revenue_at_risk`
- includes both API and browser workflows
- supports schema-mapped file uploads
- generates synthetic temporal history for trend analysis
- stores outputs in a PostgreSQL mart for BI consumption
- includes role-aware access and protected internal control surfaces

## 6. Main Screens for a Buyer Demo

### Executive Dashboard
Best for showing:
- current revenue exposure
- churn pressure
- segment balance
- top risky customers

### Monitoring Center
Best for showing:
- model governance thinking
- drift awareness
- alert visibility

### Customer Explorer
Best for showing:
- analyst workflow
- prioritisation logic
- practical customer review

### Upload Preview
Best for showing:
- flexibility beyond one hardcoded dataset
- dataset profiling and mapping
- immediate scoring feedback

### Login And Role Model
Best for showing:
- realistic internal product access
- read-only public demo mode
- separation between reviewer and internal operational access

### Admin Controls
Best for showing:
- governance thinking
- operational maturity
- internal-only control surface design

### API Docs
Best for showing:
- technical integration readiness
- realtime scoring contract

## 7. Typical Buyer Questions This Product Answers

### Which customers should be prioritised first?
Use the dashboard and customer explorer sorted by `revenue_at_risk`.

### How large is today’s revenue exposure?
Use the KPI cards and latest scoring snapshot.

### Is the model behaving differently over time?
Use the monitoring center and drift metrics.

### Can we test our own compatible customer file?
Yes, through the upload preview flow with profiling and field mapping.

### Can BI tools read the output?
Yes. The project writes to PostgreSQL marts such as `scores_daily` and `customer_snapshots`.

## 8. Current Scope vs Next Enhancements

### Already implemented
- churn model training
- batch scoring
- realtime API
- browser app
- monitoring
- PostgreSQL mart
- model registry entry registration
- schema mapping for uploaded datasets
- authenticated roles
- admin controls page

### Natural next enhancements
- admin-triggered retraining and threshold changes
- upload history persistence
- saved mapping templates
- richer buyer-facing exports

## 9. Bottom-Line Buyer Summary

This platform is a strong example of how churn prediction can be turned into a usable internal product instead of staying as an isolated ML experiment.

It is best positioned as:
- an internal churn intelligence cockpit
- a retention prioritisation tool
- a risk-aware analytics application for operational and executive review
