from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from churn_risk.api.schemas import ScoreRequest, ScoreResponse
from churn_risk.auth.service import authenticate_user, get_current_user
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
from churn_risk.ui.auth_service import build_login_context
from churn_risk.ui.admin_service import build_admin_context
from churn_risk.monitoring.data_drift import main as run_data_drift_job
from churn_risk.monitoring.prediction_drift import main as run_prediction_drift_job
from churn_risk.monitoring.threshold_alerts import main as run_threshold_alert_job
from churn_risk.train.retrain_model import main as retrain_model_job
from churn_risk.db.register_model import main as register_model_job
from churn_risk.features.build_features import main as build_features_job
from churn_risk.batch.score_batch import main as score_batch_job
from churn_risk.ingest.generate_temporal_dataset import main as generate_snapshots_job
from churn_risk.db.load_raw_to_db import main as load_raw_job
from churn_risk.db.load_features_to_db import main as load_features_job
from churn_risk.db.load_scores_to_db import main as load_scores_job
from churn_risk.db.load_snapshots_to_db import main as load_snapshots_job
from churn_risk.upload_analysis import (
    REQUIRED_UPLOAD_COLUMNS,
    apply_column_mapping,
    build_dataset_profile,
    build_mapping_options,
    get_staged_metadata,
    load_staged_dataset,
    read_uploaded_dataset,
    save_uploaded_dataset,
    score_uploaded_dataset,
)


app = FastAPI(
    title="Revenue Risk and Customer Churn Intelligence API",
    version="1.0.0",
    description=(
        "Production-style scoring API for customer churn probability and revenue-at-risk estimation."
    ),
)
templates = Jinja2Templates(directory="src/churn_risk/ui/templates")
app.mount("/static", StaticFiles(directory="src/churn_risk/ui/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)


def enrich_context(request: Request, context: dict) -> dict:
    context["request"] = request
    context["current_user"] = get_current_user(request)
    context["can_manage_upload"] = bool(
        context["current_user"] and context["current_user"]["role"] in {"analyst", "admin"}
    )
    return context


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
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "dashboard.html", context)


@app.get("/monitoring", response_class=HTMLResponse)
def monitoring_page(request: Request):
    context = build_monitoring_context()
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "monitoring.html", context)


@app.get("/customers", response_class=HTMLResponse)
def customers_page(
    request: Request,
    risk_segment: str | None = None,
    contract: str | None = None,
):
    context = build_customers_context(risk_segment=risk_segment, contract=contract)
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "customers.html", context)


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    current_user = get_current_user(request)
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    context = {
        "page_title": "Dataset Upload",
        "upload_summary": None,
        "preview_rows": [],
        "error_message": None,
        "profile_summary": None,
        "column_profiles": [],
        "mapping_fields": [],
        "staged_upload_token": None,
        "uploaded_filename": None,
        "permission_warning": None,
    }
    if current_user["role"] not in {"analyst", "admin"}:
        context["permission_warning"] = (
            "Viewer mode is read-only. You can inspect the upload workflow, but profiling and scoring "
            "actions are disabled for this account."
        )
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "upload.html", context)


@app.get("/docs/guide/", response_class=HTMLResponse)
def documentation_hub(request: Request):
    context = build_docs_hub_context()
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "documentation_hub.html", context)


@app.get("/docs/user-guide/", response_class=HTMLResponse)
def user_guide(request: Request):
    context = build_doc_page_context("user-guide")
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "documentation_page.html", context)


@app.get("/docs/manual-testing-guide/", response_class=HTMLResponse)
def manual_testing_guide(request: Request):
    context = build_doc_page_context("manual-testing-guide")
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "documentation_page.html", context)


@app.get("/docs/buyer-guide/", response_class=HTMLResponse)
def buyer_guide(request: Request):
    context = build_doc_page_context("buyer-guide")
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "documentation_page.html", context)


@app.get("/docs/upload-schema-guide/", response_class=HTMLResponse)
def upload_schema_guide(request: Request):
    context = build_doc_page_context("upload-schema-guide")
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "documentation_page.html", context)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    context = build_login_context(request)
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "login.html", context)


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if user is None:
        context = build_login_context(request, error_message="Invalid username or password.")
        context = enrich_context(request, context)
        return templates.TemplateResponse(request, "login.html", context, status_code=401)

    request.session["user"] = user
    return RedirectResponse(url="/", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


def require_admin_user(request: Request):
    current_user = get_current_user(request)
    if current_user is None:
        return None, RedirectResponse(url="/login", status_code=303)
    if current_user["role"] != "admin":
        context = build_login_context(
            request,
            error_message="Admin controls are restricted to authorised internal users.",
        )
        context = enrich_context(request, context)
        return current_user, templates.TemplateResponse(request, "login.html", context, status_code=403)
    return current_user, None


@app.get("/admin", response_class=HTMLResponse)
def admin_controls(request: Request):
    current_user, failure_response = require_admin_user(request)
    if failure_response is not None:
        return failure_response

    context = build_admin_context()
    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "admin.html", context)


@app.post("/admin/actions", response_class=HTMLResponse)
async def admin_action(request: Request, action_name: str = Form(...)):
    current_user, failure_response = require_admin_user(request)
    if failure_response is not None:
        return failure_response

    try:
        if action_name == "run_monitoring":
            run_data_drift_job()
            run_prediction_drift_job()
            run_threshold_alert_job()
            notice_message = "Monitoring suite completed successfully."
        elif action_name == "retrain_register":
            retrain_model_job()
            register_model_job()
            notice_message = "Model retraining and registry update completed successfully."
        elif action_name == "refresh_mart":
            build_features_job()
            score_batch_job()
            generate_snapshots_job()
            load_raw_job()
            load_features_job()
            load_scores_job()
            load_snapshots_job()
            notice_message = "Analytics mart refresh completed successfully."
        else:
            raise ValueError(f"Unknown admin action: {action_name}")

        context = build_admin_context(notice_message=notice_message, notice_tone="success")
    except Exception as exc:  # noqa: BLE001
        context = build_admin_context(
            notice_message=f"Admin action failed: {exc}",
            notice_tone="error",
        )

    context = enrich_context(request, context)
    return templates.TemplateResponse(request, "admin.html", context)


@app.post("/upload", response_class=HTMLResponse)
async def upload_dataset(request: Request, dataset_file: UploadFile = File(...)):
    current_user = get_current_user(request)
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    context = {
        "page_title": "Dataset Upload",
        "upload_summary": None,
        "preview_rows": [],
        "error_message": None,
        "profile_summary": None,
        "column_profiles": [],
        "mapping_fields": [],
        "staged_upload_token": None,
        "uploaded_filename": None,
        "permission_warning": None,
    }
    context = enrich_context(request, context)
    if current_user["role"] not in {"analyst", "admin"}:
        context["permission_warning"] = (
            "Upload actions are not permitted in viewer mode. This account can review the page, but "
            "profiling and scoring uploads require an authorised internal role."
        )
        return templates.TemplateResponse(request, "upload.html", context, status_code=403)

    try:
        file_content = await dataset_file.read()
        uploaded_df = read_uploaded_dataset(dataset_file.filename or "uploaded.csv", file_content)
        staged_token = save_uploaded_dataset(uploaded_df, dataset_file.filename or "uploaded.csv")
        profile_summary = build_dataset_profile(uploaded_df)
        mapping_fields = build_mapping_options(uploaded_df, profile_summary["mapping_suggestions"])
        context["profile_summary"] = profile_summary
        context["column_profiles"] = profile_summary["column_profiles"]
        context["mapping_fields"] = mapping_fields
        context["staged_upload_token"] = staged_token
        context["uploaded_filename"] = dataset_file.filename or "uploaded.csv"
    except Exception as exc:  # noqa: BLE001
        context["error_message"] = str(exc)

    return templates.TemplateResponse(request, "upload.html", context)


@app.post("/upload/score-mapped", response_class=HTMLResponse)
async def upload_score_mapped(
    request: Request,
    staged_upload_token: str = Form(...),
    customerID: str = Form(""),
    gender: str = Form(""),
    SeniorCitizen: str = Form(""),
    Partner: str = Form(""),
    Dependents: str = Form(""),
    tenure: str = Form(""),
    PhoneService: str = Form(""),
    MultipleLines: str = Form(""),
    InternetService: str = Form(""),
    OnlineSecurity: str = Form(""),
    OnlineBackup: str = Form(""),
    DeviceProtection: str = Form(""),
    TechSupport: str = Form(""),
    StreamingTV: str = Form(""),
    StreamingMovies: str = Form(""),
    Contract: str = Form(""),
    PaperlessBilling: str = Form(""),
    PaymentMethod: str = Form(""),
    MonthlyCharges: str = Form(""),
    TotalCharges: str = Form(""),
):
    current_user = get_current_user(request)
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    mapping = {
        field: value
        for field, value in {
            "customerID": customerID,
            "gender": gender,
            "SeniorCitizen": SeniorCitizen,
            "Partner": Partner,
            "Dependents": Dependents,
            "tenure": tenure,
            "PhoneService": PhoneService,
            "MultipleLines": MultipleLines,
            "InternetService": InternetService,
            "OnlineSecurity": OnlineSecurity,
            "OnlineBackup": OnlineBackup,
            "DeviceProtection": DeviceProtection,
            "TechSupport": TechSupport,
            "StreamingTV": StreamingTV,
            "StreamingMovies": StreamingMovies,
            "Contract": Contract,
            "PaperlessBilling": PaperlessBilling,
            "PaymentMethod": PaymentMethod,
            "MonthlyCharges": MonthlyCharges,
            "TotalCharges": TotalCharges,
        }.items()
    }
    context = {
        "page_title": "Dataset Upload",
        "upload_summary": None,
        "preview_rows": [],
        "error_message": None,
        "profile_summary": None,
        "column_profiles": [],
        "mapping_fields": [],
        "staged_upload_token": staged_upload_token,
        "uploaded_filename": None,
        "permission_warning": None,
    }
    context = enrich_context(request, context)
    if current_user["role"] not in {"analyst", "admin"}:
        context["permission_warning"] = (
            "Mapped scoring is disabled in viewer mode. This account can inspect the workflow but cannot "
            "run upload-based scoring actions."
        )
        return templates.TemplateResponse(request, "upload.html", context, status_code=403)

    try:
        uploaded_df = load_staged_dataset(staged_upload_token)
        metadata = get_staged_metadata(staged_upload_token)
        mapped_df = apply_column_mapping(uploaded_df, mapping)
        model, preprocessor = get_inference_assets()
        summary, preview_rows = score_uploaded_dataset(mapped_df, model, preprocessor)

        profile_summary = build_dataset_profile(uploaded_df)
        context["profile_summary"] = profile_summary
        context["column_profiles"] = profile_summary["column_profiles"]
        context["mapping_fields"] = build_mapping_options(uploaded_df, mapping)
        context["upload_summary"] = summary
        context["preview_rows"] = preview_rows
        context["uploaded_filename"] = metadata.get("original_filename")
    except Exception as exc:  # noqa: BLE001
        try:
            uploaded_df = load_staged_dataset(staged_upload_token)
            profile_summary = build_dataset_profile(uploaded_df)
            context["profile_summary"] = profile_summary
            context["column_profiles"] = profile_summary["column_profiles"]
            context["mapping_fields"] = build_mapping_options(uploaded_df, mapping)
            metadata = get_staged_metadata(staged_upload_token)
            context["uploaded_filename"] = metadata.get("original_filename")
        except Exception:
            pass
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
