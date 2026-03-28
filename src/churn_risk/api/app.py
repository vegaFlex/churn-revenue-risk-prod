from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from churn_risk.api.schemas import ScoreRequest, ScoreResponse
from churn_risk.config import settings
from churn_risk.scoring import (
    build_model_input,
    build_score_output,
    load_inference_artifacts,
    predict_churn_probabilities,
)
from churn_risk.ui.customers_service import build_customers_context
from churn_risk.ui.dashboard_service import build_dashboard_context
from churn_risk.ui.docs_service import build_doc_page_context, build_docs_hub_context
from churn_risk.ui.monitoring_service import build_monitoring_context
from churn_risk.ui.upload_service import score_uploaded_dataset


app = FastAPI(
    title="Revenue Risk and Customer Churn Intelligence API",
    version="1.0.0",
    description=(
        "Production-style scoring API for customer churn probability and revenue-at-risk estimation."
    ),
)
templates = Jinja2Templates(directory="src/churn_risk/ui/templates")
app.mount("/static", StaticFiles(directory="src/churn_risk/ui/static"), name="static")


@lru_cache
def get_inference_assets():
    return load_inference_artifacts(settings.model_path, settings.preprocessor_path)


def build_request_features(payload: ScoreRequest) -> pd.DataFrame:
    row = pd.DataFrame([payload.model_dump()])
    row["TotalCharges"] = pd.to_numeric(row["TotalCharges"], errors="coerce")
    row["TotalCharges"] = row["TotalCharges"].fillna(row["MonthlyCharges"] * row["tenure"])
    row["tenure_bucket"] = pd.cut(
        row["tenure"],
        bins=[-1, 12, 24, 48, 72],
        labels=["0_12", "13_24", "25_48", "49_72"],
    ).astype(str)
    row["contract_term_months"] = row["Contract"].map(
        {
            "Month-to-month": 1,
            "One year": 12,
            "Two year": 24,
        }
    ).astype("int64")
    row["monthly_charges_log"] = np.log1p(row["MonthlyCharges"])
    row["has_internet"] = (row["InternetService"] != "No").astype("int64")
    row["has_security"] = (row["OnlineSecurity"] == "Yes").astype("int64")
    row["payment_risk_flag"] = (row["PaymentMethod"] == "Electronic check").astype("int64")
    row["is_senior"] = row["SeniorCitizen"].astype("int64")
    row["has_partner"] = (row["Partner"] == "Yes").astype("int64")
    row["has_dependents"] = (row["Dependents"] == "Yes").astype("int64")
    return row


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    context = build_dashboard_context()
    context["request"] = request
    return templates.TemplateResponse(request, "dashboard.html", context)


@app.get("/monitoring", response_class=HTMLResponse)
def monitoring_page(request: Request):
    context = build_monitoring_context()
    context["request"] = request
    return templates.TemplateResponse(request, "monitoring.html", context)


@app.get("/customers", response_class=HTMLResponse)
def customers_page(
    request: Request,
    risk_segment: str | None = None,
    contract: str | None = None,
):
    context = build_customers_context(risk_segment=risk_segment, contract=contract)
    context["request"] = request
    return templates.TemplateResponse(request, "customers.html", context)


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    context = {
        "page_title": "Dataset Upload",
        "request": request,
        "upload_summary": None,
        "preview_rows": [],
        "error_message": None,
    }
    return templates.TemplateResponse(request, "upload.html", context)


@app.get("/docs/guide/", response_class=HTMLResponse)
def documentation_hub(request: Request):
    context = build_docs_hub_context()
    context["request"] = request
    return templates.TemplateResponse(request, "documentation_hub.html", context)


@app.get("/docs/user-guide/", response_class=HTMLResponse)
def user_guide(request: Request):
    context = build_doc_page_context("user-guide")
    context["request"] = request
    return templates.TemplateResponse(request, "documentation_page.html", context)


@app.get("/docs/manual-testing-guide/", response_class=HTMLResponse)
def manual_testing_guide(request: Request):
    context = build_doc_page_context("manual-testing-guide")
    context["request"] = request
    return templates.TemplateResponse(request, "documentation_page.html", context)


@app.get("/docs/buyer-guide/", response_class=HTMLResponse)
def buyer_guide(request: Request):
    context = build_doc_page_context("buyer-guide")
    context["request"] = request
    return templates.TemplateResponse(request, "documentation_page.html", context)


@app.post("/upload", response_class=HTMLResponse)
async def upload_dataset(request: Request, dataset_file: UploadFile = File(...)):
    context = {
        "page_title": "Dataset Upload",
        "request": request,
        "upload_summary": None,
        "preview_rows": [],
        "error_message": None,
    }

    try:
        model, preprocessor = get_inference_assets()
        file_content = await dataset_file.read()
        from churn_risk.ui.upload_service import read_uploaded_dataset

        uploaded_df = read_uploaded_dataset(dataset_file.filename or "uploaded.csv", file_content)
        summary, preview_rows = score_uploaded_dataset(uploaded_df, model, preprocessor)
        context["upload_summary"] = summary
        context["preview_rows"] = preview_rows
    except Exception as exc:  # noqa: BLE001
        context["error_message"] = str(exc)

    return templates.TemplateResponse(request, "upload.html", context)


@app.post("/score", response_model=ScoreResponse)
def score_customer(payload: ScoreRequest) -> ScoreResponse:
    model, preprocessor = get_inference_assets()
    feature_row = build_request_features(payload)
    model_input = build_model_input(feature_row)
    churn_probability = predict_churn_probabilities(model_input, model, preprocessor)
    scored_row = build_score_output(feature_row, churn_probability)
    result = scored_row.iloc[0]

    return ScoreResponse(
        customer_id=result["customerID"],
        churn_probability=round(float(result["churn_probability"]), 6),
        monthly_revenue=round(float(result["monthly_revenue"]), 2),
        expected_months_remaining=round(float(result["expected_months_remaining"]), 2),
        revenue_at_risk=round(float(result["revenue_at_risk"]), 2),
        risk_segment=str(result["risk_segment"]),
    )
