from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class ApplicantType(str, Enum):
    UNBANKED = "unbanked"
    UNDERBANKED = "underbanked"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


# ---------------------------------------------------------------------------
# Decision mode types (research paper: D1–D4)
# ---------------------------------------------------------------------------

class DecisionMode(str, Enum):
    D1 = "D1"   # ML Risk Model only
    D2 = "D2"   # ML + Policy Eligibility
    D3 = "D3"   # ML + Evidence Quality
    D4 = "D4"   # ML + Policy + Evidence (full system)


class DecisionOutcome(str, Enum):
    APPROVE = "APPROVE"
    REVIEW  = "REVIEW"
    DECLINE = "DECLINE"


class EvidenceResponse(BaseModel):
    score: float
    status: str          # "SUFFICIENT" | "INSUFFICIENT"
    history_months: int
    aa_completeness: float
    uli_completeness: float
    threshold: float


class PolicyRuleResult(BaseModel):
    rule_id: str
    condition: str
    state: str
    attribute_value: Optional[str] = None
    note: str = ""


class PolicyResponse(BaseModel):
    scheme: str
    state: str           # "SATISFIED" | "UNSATISFIED" | "UNRESOLVED"
    reason: str
    rule_results: List[PolicyRuleResult] = []
    provenance_note: str = ""


class AlternativeDataInput(BaseModel):
    # Common fields
    monthly_income: Optional[float] = Field(None, ge=0)
    monthly_expenses: Optional[float] = Field(None, ge=0)
    utility_payment_history: Optional[str] = None
    employment_type: Optional[str] = None
    employment_stability_years: Optional[float] = Field(None, ge=0, le=50)
    number_of_dependents: Optional[int] = Field(None, ge=0, le=20)
    existing_loan_count: Optional[int] = Field(None, ge=0)
    loan_repayment_history_score: Optional[float] = Field(None, ge=0, le=10)
    utility_bill_payment_score: Optional[float] = Field(None, ge=0, le=10)

    # Unbanked specific
    remittance_frequency: Optional[int] = Field(None, ge=0)
    community_verification_score: Optional[float] = Field(None, ge=0, le=10)
    microfinance_repayment_count: Optional[int] = Field(None, ge=0)
    
    # Underbanked specific
    gig_platform_rating: Optional[float] = Field(None, ge=0, le=5)
    upi_transaction_frequency: Optional[int] = Field(None, ge=0)
    savings_account_balance: Optional[float] = Field(None, ge=0)


class CreditApplicationCreate(BaseModel):
    applicant_type: ApplicantType
    full_name: str
    age: int = Field(..., ge=18, le=100)
    phone_number: str
    address: str
    requested_amount: float = Field(..., gt=0)
    loan_purpose: str
    alternative_data: AlternativeDataInput
    document_links: Optional[dict] = None
    # Research paper: which decision mode to use (default D4 = full system)
    decision_mode: DecisionMode = DecisionMode.D4


class CreditApplicationResponse(BaseModel):
    application_id: int
    user_id: int
    applicant_type: ApplicantType
    status: ApplicationStatus
    requested_amount: float
    credit_score: Optional[float] = None
    risk_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Research paper: new fields
    decision_mode: Optional[str] = None
    decision: Optional[str] = None
    reason_code: Optional[str] = None
    evidence: Optional[EvidenceResponse] = None
    policy: Optional[PolicyResponse] = None

    class Config:
        from_attributes = True


class SHAPExplanation(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float
    impact: str


class CreditScoreDetail(BaseModel):
    application_id: int
    credit_score: float
    default_probability: float
    risk_category: str
    shap_explanations: List[SHAPExplanation]
    model_version: str
    created_at: datetime
    
    class Config:
        from_attributes = True
