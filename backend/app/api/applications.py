from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.application import (
    CreditApplicationCreate,
    CreditApplicationResponse,
    CreditScoreDetail,
    ApplicationStatus
)
from app.services.credit_service import CreditService
from app.services.prediction_service import PredictionService
from app.utils.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.application import Application
from app.models.credit_score import CreditScore
from app.config import settings

router = APIRouter(prefix="/applications", tags=["applications"])


def get_prediction_service():
    """Dependency for prediction service"""
    return PredictionService(
        model_path=settings.MODEL_PATH,
        shap_explainer_path=settings.SHAP_EXPLAINER_PATH,
        feature_names_path=settings.FEATURE_NAMES_PATH
    )


@router.post("", response_model=CreditApplicationResponse, status_code=201)
async def create_application(
    application_data: CreditApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Submit new credit application"""
    credit_service = CreditService(db, prediction_service)
    return credit_service.create_application(current_user.id, application_data)


@router.get("", response_model=List[CreditApplicationResponse])
async def list_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """List user's applications"""
    credit_service = CreditService(db, prediction_service)
    return credit_service.list_user_applications(current_user.id, skip, limit)


@router.get("/{application_id}", response_model=CreditApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Get application details"""
    credit_service = CreditService(db, prediction_service)
    is_admin = current_user.role == "admin"
    return credit_service.get_application(application_id, current_user.id, is_admin)


@router.get("/{application_id}/score", response_model=CreditScoreDetail)
async def get_credit_score(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get credit score details with SHAP explanations"""
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Authorization check
    is_admin = current_user.role == "admin"
    if not is_admin and application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not application.credit_score:
        raise HTTPException(status_code=404, detail="Credit score not yet generated")
    
    return application.credit_score
