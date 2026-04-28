from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.application import CreditApplicationResponse, ApplicationStatus
from app.services.credit_service import CreditService
from app.services.prediction_service import PredictionService
from app.utils.dependencies import get_current_admin
from app.models.user import User
from app.models.application import Application
from app.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/admin-legacy", tags=["admin-legacy"])


def get_prediction_service():
    """Dependency for prediction service"""
    return PredictionService(
        model_path=settings.MODEL_PATH,
        shap_explainer_path=settings.SHAP_EXPLAINER_PATH,
        feature_names_path=settings.FEATURE_NAMES_PATH
    )


class StatusUpdate(BaseModel):
    status: ApplicationStatus


class PlatformStatistics(BaseModel):
    total_applications: int
    approved: int
    rejected: int
    under_review: int
    pending: int
    average_credit_score: float
    total_users: int


@router.get("/applications", response_model=List[CreditApplicationResponse])
async def list_all_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """List all applications (admin only)"""
    credit_service = CreditService(db, prediction_service)
    return credit_service.list_all_applications(skip, limit, status)


@router.put("/applications/{application_id}/status", response_model=CreditApplicationResponse)
async def update_application_status(
    application_id: int,
    status_update: StatusUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Update application status (admin only)"""
    credit_service = CreditService(db, prediction_service)
    return credit_service.update_application_status(application_id, status_update.status)


@router.get("/statistics", response_model=PlatformStatistics)
async def get_statistics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics (admin only)"""
    from sqlalchemy import func
    from app.models.credit_score import CreditScore
    
    total_applications = db.query(Application).count()
    approved = db.query(Application).filter(Application.status == "approved").count()
    rejected = db.query(Application).filter(Application.status == "rejected").count()
    under_review = db.query(Application).filter(Application.status == "under_review").count()
    pending = db.query(Application).filter(Application.status == "pending").count()
    
    avg_score = db.query(func.avg(CreditScore.credit_score)).scalar()
    average_credit_score = float(avg_score) if avg_score else 0.0
    
    total_users = db.query(User).count()
    
    return PlatformStatistics(
        total_applications=total_applications,
        approved=approved,
        rejected=rejected,
        under_review=under_review,
        pending=pending,
        average_credit_score=average_credit_score,
        total_users=total_users
    )
