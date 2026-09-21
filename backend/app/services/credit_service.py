from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.application import Application
from app.models.credit_score import CreditScore
from app.schemas.application import (
    CreditApplicationCreate,
    CreditApplicationResponse,
    ApplicationStatus,
    EvidenceResponse,
    PolicyResponse,
    PolicyRuleResult,
)
from app.services.prediction_service import PredictionService
from app.services.evidence_service import compute_evidence, derive_evidence_inputs
from app.services.policy_service import evaluate_policy, derive_policy_inputs
from app.services.decision_service import make_decision, DEFAULT_TAU


class CreditService:
    def __init__(self, db: Session, prediction_service: PredictionService):
        self.db = db
        self.prediction_service = prediction_service
    
    def create_application(self, user_id: int, application_data: CreditApplicationCreate) -> CreditApplicationResponse:
        """Create new credit application and trigger scoring"""
        # Validate at least 3 alternative data fields
        alt_data_dict = application_data.alternative_data.dict(exclude_none=True)
        if len(alt_data_dict) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 3 alternative data fields required"
            )

        # Create application record
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

        try:
            # ----------------------------------------------------------------
            # Layer 1 — ML Risk Model (existing)
            # ----------------------------------------------------------------
            features    = self.prediction_service.engineer_features(application_data)
            score_result = self.prediction_service.predict_credit_score(features)

            # ----------------------------------------------------------------
            # Layer 2 — Evidence Quality Engine
            # ----------------------------------------------------------------
            alt_dict = application_data.alternative_data.dict()
            ev_inputs = derive_evidence_inputs(alt_dict, application_data.applicant_type.value)
            evidence  = compute_evidence(**ev_inputs)

            # ----------------------------------------------------------------
            # Layer 3 — Policy Rule Engine
            # ----------------------------------------------------------------
            monthly_income = float(alt_dict.get("monthly_income") or 0)
            pol_inputs = derive_policy_inputs(
                age=application_data.age,
                alternative_data=alt_dict,
                applicant_type=application_data.applicant_type.value,
                monthly_income=monthly_income,
            )
            policy = evaluate_policy(**pol_inputs)

            # ----------------------------------------------------------------
            # Layer 4 — Decision Engine (D1–D4)
            # ----------------------------------------------------------------
            decision_result = make_decision(
                pd=score_result.default_probability,
                mode=application_data.decision_mode.value,
                evidence=evidence,
                policy=policy,
                tau=DEFAULT_TAU,
            )

            # Map decision outcome to application status
            status_map = {
                "APPROVE": "approved",
                "REVIEW":  "under_review",
                "DECLINE": "rejected",
            }
            application.status = status_map.get(decision_result.decision, "under_review")

            # Store credit score record
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

            return self._to_response(application, decision_result, evidence, policy)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Prediction/decision failed: {e}")
            application.status = "under_review"
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Credit scoring temporarily unavailable: {str(e)}"
            )
    
    def get_application(self, application_id: int, user_id: int, is_admin: bool = False) -> CreditApplicationResponse:
        """Retrieve application by ID with authorization check"""
        application = self.db.query(Application).filter(Application.id == application_id).first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

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

    def _to_response(self, application: Application, decision_result=None,
                     evidence=None, policy=None) -> CreditApplicationResponse:
        """Convert Application model to response schema"""
        credit_score_value = None
        risk_category = None

        if application.credit_score:
            credit_score_value = application.credit_score.credit_score
            risk_category      = application.credit_score.risk_category

        # Build evidence and policy sub-objects if available
        evidence_resp = None
        if evidence:
            evidence_resp = EvidenceResponse(**evidence.to_dict())

        policy_resp = None
        if policy:
            policy_resp = PolicyResponse(
                scheme=policy.scheme,
                state=policy.state.value,
                reason=policy.reason,
                rule_results=[
                    PolicyRuleResult(
                        rule_id=r.rule_id,
                        condition=r.condition,
                        state=r.state.value,
                        attribute_value=r.attribute_value,
                        note=r.note,
                    )
                    for r in policy.rule_results
                ],
                provenance_note=policy.provenance_note,
            )

        return CreditApplicationResponse(
            application_id=application.id,
            user_id=application.user_id,
            applicant_type=application.applicant_type,
            status=application.status,
            requested_amount=application.requested_amount,
            credit_score=credit_score_value,
            risk_category=risk_category,
            created_at=application.created_at,
            updated_at=application.updated_at,
            decision_mode=decision_result.mode if decision_result else None,
            decision=decision_result.decision if decision_result else None,
            reason_code=decision_result.reason_code if decision_result else None,
            evidence=evidence_resp,
            policy=policy_resp,
        )
