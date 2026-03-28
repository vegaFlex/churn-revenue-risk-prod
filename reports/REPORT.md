# Revenue Risk and Customer Churn Intelligence Report

## Data Source
- Public telco churn dataset from IBM
- Raw source file: `Telco-Customer-Churn.csv`
- Customer records used: `7,043`

## Method
This project was built as a production-style churn intelligence system, not just a modeling notebook.

The workflow:
- ingested and validated the telco customer dataset
- engineered churn and revenue-risk features
- trained and benchmarked classification models
- selected the best model by AUC
- generated customer-level batch scores
- estimated expected months remaining and revenue-at-risk
- created a PostgreSQL risk mart
- generated temporal snapshots for trend analysis
- added drift monitoring and threshold alerts
- exposed both API scoring and browser-based review pages

Selected model:
- `Random Forest`

Model metrics:
- AUC: `0.8420`
- Precision: `0.5402`
- Recall: `0.7540`
- F1: `0.6295`

## Key Findings
1. Total current revenue at risk is `$622,385.88`, which shows that churn is not just a retention metric but a material revenue exposure signal.
2. The average predicted churn probability in the latest batch snapshot is `37.8%`, which indicates a meaningful concentration of at-risk customers in the portfolio.
3. `1,455` customers are currently classified as `high` risk in the latest scoring run, creating a strong priority pool for retention interventions.
4. The highest individual customer revenue-at-risk values are concentrated above `$690`, with the top three customers at `$713.77`, `$694.38`, and `$690.59`.
5. Monitoring signals already show operational pressure: `total_revenue_at_risk` is above the configured alert threshold, and both `avg_churn_probability_delta` and `high_risk_share_delta` are flagged as alerts in the latest monitoring snapshot.

## Recommended Actions
1. Create a high-risk retention campaign for the top `1,455` customers, prioritising customers with both high churn probability and high monthly revenue.
2. Introduce contract and payment-method interventions, especially for customers on `Month-to-month` contracts and `Electronic check`, because these features are directly reflected in the risk pipeline.
3. Review alert thresholds and monitoring cadence weekly, especially where `prediction_drift` and `threshold_alert` metrics are already crossing limits.

## Limitations
- The source dataset is a public benchmark dataset and not a real production event stream.
- `expected_months_remaining` is currently based on business heuristics rather than a dedicated survival model.
- Temporal customer history is synthetic and was generated to support monitoring, browser analytics, and trend views.
- Compatible upload mode currently expects a telco-aligned schema and does not yet include a full schema-mapping interface.
