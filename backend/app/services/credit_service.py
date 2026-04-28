from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.application import Application
from app.models.credit_score import CreditScore
from app.schemas.application import (
    CreditApplicationCreate, 
    CreditApplicationResponse,
    ApplicationStatus
)
from app.services.prediction_service import PredictionService


class CreditService:
    def __init__(self, db: Session, prediction_service: PredictionService):
        self.db = db
        self.prediction_service = prediction_service
    
    def create_application(self, user_id: int, application_data: CreditApplicationCreate) -> CreditApplicationResponse:
        """Create new credit application and trigger scoring"""
        # Check rate limit (3 applications per 30 days) - DISABLED FOR DEMO
        # thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        # recent_apps = self.db.query(Application).filter(
        #     Application.user_id == user_id,
        #     Application.created_at >= thirty_days_ago
        # ).count()
        
        # if recent_apps >= 3:
        #     raise HTTPException(
        #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        #         detail="Maximum 3 applications per month allowed"
        #     )
        
        # Validate at least 3 alternative data fields
        alt_data_dict = application_data.alternative_data.dict(exclude_none=True)
        if len(alt_data_dict) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 3 alternative data fields required"
            )
        
        # Create application
        application = Application(
            user_id=user_id,
            applicant_type=application_data.applicant_type.value,
            full_name=application_data.full_name,
            age=application_data.age,
            phone_number=application_data.phone_number,
            address=application_data.address,
            requested_amount=application_data.requested_amount,
            loan_purpose=application_data.loan_purpose,
            alternative_data=application_data.alternative_data.dict(),
            document_links=application_data.document_links or {},
            status="pending"
        )
        
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        
        # Generate credit score
        try:
            features = self.prediction_service.engineer_features(application_data)
            score_result = self.prediction_service.predict_credit_score(features)
            
            # Store credit score
            credit_score = CreditScore(
                application_id=application.id,
                credit_score=score_result.credit_score,
                default_probability=score_result.default_probability,
                risk_category=score_result.risk_category,
                shap_explanations=[exp.dict() for exp in score_result.shap_explanations],
                model_version=score_result.model_version
            )
            
            self.db.add(credit_score)
            self.db.commit()
            self.db.refresh(application)
            
        except Exception as e:
            print(f"Prediction failed: {e}")
            application.status = "under_review"
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Credit scoring temporarily unavailable"
            )
        
        return self._to_response(application)
    
    def get_application(self, application_id: int, user_id: int, is_admin: bool = False) -> CreditApplicationResponse:
        """Retrieve application by ID with authorization check"""
        application = self.db.query(Application).filter(Application.id == application_id).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Authorization check
        if not is_admin and application.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
        
        return self._to_response(application)
    
    def list_user_applications(self, user_id: int, skip: int = 0, limit: int = 100) -> List[CreditApplicationResponse]:
        """List all applications for a user"""
        applications = self.db.query(Application).filter(
            Application.user_id == user_id
        ).order_by(Application.created_at.desc()).offset(skip).limit(limit).all()
        
        return [self._to_response(app) for app in applications]
    
    def list_all_applications(self, skip: int = 0, limit: int = 100, 
                            status_filter: Optional[str] = None) -> List[CreditApplicationResponse]:
        """List all applications (admin only)"""
        query = self.db.query(Application)
        
        if status_filter:
            query = query.filter(Application.status == status_filter)
        
        applications = query.order_by(Application.created_at.desc()).offset(skip).limit(limit).all()
        
        return [self._to_response(app) for app in applications]
    
    def update_application_status(self, application_id: int, new_status: ApplicationStatus) -> CreditApplicationResponse:
        """Update application status (admin only)"""
        application = self.db.query(Application).filter(Application.id == application_id).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        application.status = new_status.value
        self.db.commit()
        self.db.refresh(application)
        
        return self._to_response(application)
    
    def _to_response(self, application: Application) -> CreditApplicationResponse:
        """Convert Application model to response schema"""
        credit_score_value = None
        risk_category = None
        
        if application.credit_score:
            credit_score_value = application.credit_score.credit_score
            risk_category = application.credit_score.risk_category
        
        return CreditApplicationResponse(
            application_id=application.id,
            user_id=application.user_id,
            applicant_type=application.applicant_type,
            status=application.status,
            requested_amount=application.requested_amount,
            credit_score=credit_score_value,
            risk_category=risk_category,
            created_at=application.created_at,
            updated_at=application.updated_at
        )
