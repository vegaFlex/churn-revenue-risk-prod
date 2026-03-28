# Revenue Risk and Customer Churn Intelligence Platform - Upload Schema Guide

## 1. Purpose

This guide explains how uploaded datasets are validated before they can be scored by the churn and revenue-risk engine.

## 2. What the App Supports Today

The current upload workflow supports:
- CSV files
- Parquet files
- Excel files (`.xlsx`)

The app does not require the uploaded dataset to use the exact same column names as the original telco dataset.

Instead, it now supports:
- dataset profiling
- suggested schema mapping
- manual field mapping before scoring

## 3. Required Business Fields

To run churn scoring, the uploaded file must eventually provide mappings for these required fields:

- `customerID`
- `gender`
- `SeniorCitizen`
- `Partner`
- `Dependents`
- `tenure`
- `PhoneService`
- `MultipleLines`
- `InternetService`
- `OnlineSecurity`
- `OnlineBackup`
- `DeviceProtection`
- `TechSupport`
- `StreamingTV`
- `StreamingMovies`
- `Contract`
- `PaperlessBilling`
- `PaymentMethod`
- `MonthlyCharges`
- `TotalCharges`

If the app cannot map these fields, scoring cannot run.

## 4. Example Synonyms the App Can Suggest

Examples of automatically suggested matches:

- `client_id` -> `customerID`
- `sex` -> `gender`
- `senior_flag` -> `SeniorCitizen`
- `months_active` -> `tenure`
- `monthly_fee` -> `MonthlyCharges`
- `total_billed` -> `TotalCharges`
- `contract_type` -> `Contract`
- `billing_method` -> `PaymentMethod`

The suggestions are only helpers. Users can override them manually before scoring.

## 5. Access And Execution Rules

The upload page is role-aware:
- `viewer` can inspect the workflow in read-only mode
- `analyst` can run profiling and mapped scoring
- `admin` can run profiling and mapped scoring and access future protected controls

This means that seeing the page is not the same as being allowed to execute upload actions.

## 6. Expected Value Style

The current scoring engine works best when mapped values look similar to the telco-compatible format.

Examples:

- `gender`: `Male` / `Female`
- `SeniorCitizen`: `0` / `1`
- `Partner`: `Yes` / `No`
- `Dependents`: `Yes` / `No`
- `tenure`: whole number of months
- `Contract`: `Month-to-month`, `One year`, `Two year`
- `MonthlyCharges`: numeric
- `TotalCharges`: numeric

## 7. What Happens During Upload

1. The file is uploaded
2. The app profiles rows, columns, missingness, and data types
3. The app suggests possible field mappings
4. The user confirms or corrects the mapping
5. The app validates that all required scoring fields are present
6. The app engineers features and runs the trained churn model
7. The app returns KPI summary and a preview of top risky customers

## 8. What Is Not Supported Yet

The current workflow does not yet support:
- fully automatic scoring for arbitrary targets
- generic AutoML across unrelated business problems
- saved upload history in the browser app
- reusable saved mapping templates per dataset family

## 9. Best-Practice Upload Advice

For the best scoring experience:
- use one row per customer
- keep categorical values consistent
- use numeric values for charges and tenure
- avoid mixing multiple business entities in the same file
- review the mapping suggestions before running scoring

## 10. Common Reasons Scoring Fails

Typical causes:
- one or more required business fields are still unmapped
- numeric columns contain unparseable values
- uploaded data is too different from the expected telco-style customer profile
- business values use unsupported categories without cleanup
- the logged-in account is in read-only viewer mode

## 11. Recommended Next Step for Broader Support

If wider dataset support is needed, the natural enhancement is:
- saved schema templates
- richer categorical normalization
- upload history and run persistence
- optional generic profiling mode separate from churn scoring
