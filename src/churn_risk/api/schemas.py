from __future__ import annotations

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    customerID: str = Field(..., examples=["7590-VHVEG"])
    gender: str = Field(..., examples=["Female"])
    SeniorCitizen: int = Field(..., ge=0, le=1, examples=[0])
    Partner: str = Field(..., examples=["Yes"])
    Dependents: str = Field(..., examples=["No"])
    tenure: int = Field(..., ge=0, le=72, examples=[12])
    PhoneService: str = Field(..., examples=["Yes"])
    MultipleLines: str = Field(..., examples=["No"])
    InternetService: str = Field(..., examples=["Fiber optic"])
    OnlineSecurity: str = Field(..., examples=["No"])
    OnlineBackup: str = Field(..., examples=["Yes"])
    DeviceProtection: str = Field(..., examples=["No"])
    TechSupport: str = Field(..., examples=["No"])
    StreamingTV: str = Field(..., examples=["Yes"])
    StreamingMovies: str = Field(..., examples=["Yes"])
    Contract: str = Field(..., examples=["Month-to-month"])
    PaperlessBilling: str = Field(..., examples=["Yes"])
    PaymentMethod: str = Field(..., examples=["Electronic check"])
    MonthlyCharges: float = Field(..., gt=0, examples=[89.45])
    TotalCharges: float = Field(..., ge=0, examples=[1073.40])


class ScoreResponse(BaseModel):
    customer_id: str
    churn_probability: float
    monthly_revenue: float
    expected_months_remaining: float
    revenue_at_risk: float
    risk_segment: str
