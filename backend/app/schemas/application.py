from pydantic import BaseModel, Field
from typing import Optional, List
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


class AlternativeDataInput(BaseModel):
    # Common fields
    monthly_income: Optional[float] = Field(None, ge=0)
    utility_payment_history: Optional[str] = None
    employment_type: Optional[str] = None
    
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
