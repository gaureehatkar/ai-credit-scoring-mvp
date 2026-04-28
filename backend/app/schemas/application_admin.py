from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., description="New status for the application")
    notes: Optional[str] = Field(None, max_length=500)
    reason: Optional[str] = Field(None, max_length=500)


class ApplicationDetailResponse(BaseModel):
    application_id: int
    user_id: int
    applicant_type: str
    full_name: str
    age: int
    phone_number: str
    address: str
    requested_amount: float
    loan_purpose: str
    alternative_data: dict
    status: str
    credit_score: Optional[float] = None
    risk_category: Optional[str] = None
    document_links: Optional[dict] = None
    consistency_flags: Optional[list] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='before')
    @classmethod
    def set_application_id(cls, data):
        if isinstance(data, dict):
            if 'application_id' not in data and 'id' in data:
                data['application_id'] = data['id']
        return data

    class Config:
        from_attributes = True
