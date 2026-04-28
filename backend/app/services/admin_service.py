from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict
from app.models.admin_user import AdminUser
from app.models.audit_log import AuditLog
from app.models.application import Application
from app.models.credit_score import CreditScore
from app.models.user import User
from app.schemas.admin import AdminUserCreate, AdminUserResponse
from app.utils.security import hash_password
from app.services.email_service import EmailService
from datetime import datetime


class AdminService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_admin_user(
        self,
        admin_data: AdminUserCreate,
        current_admin: AdminUser
    ) -> Dict:
        """Create new admin user with specified role and permissions"""
        # Verify current admin is super_admin
        if current_admin.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super_admin can create admin users"
            )
        
        # Check email uniqueness
        existing_admin = self.db.query(AdminUser).filter(
            AdminUser.email == admin_data.email
        ).first()
        
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        
        # Validate password length
        if len(admin_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Validate role
        if admin_data.role not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be either 'admin' or 'super_admin'"
            )
        
        # Hash password
        password_hash = hash_password(admin_data.password)
        
        # Create new admin user
        new_admin = AdminUser(
            email=admin_data.email,
            full_name=admin_data.full_name,
            password_hash=password_hash,
            role=admin_data.role,
            permissions=admin_data.permissions or [],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(new_admin)
        self.db.flush()  # Flush to get the admin_id
        
        # Create audit log entry
        audit_log = AuditLog(
            admin_id=current_admin.admin_id,
            action="create_admin",
            resource_type="admin_user",
            resource_id=new_admin.admin_id,
            old_value=None,
            new_value={
                "email": new_admin.email,
                "full_name": new_admin.full_name,
                "role": new_admin.role,
                "permissions": new_admin.permissions
            },
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return {
            "admin_id": new_admin.admin_id,
            "email": new_admin.email,
            "full_name": new_admin.full_name,
            "role": new_admin.role,
            "permissions": new_admin.permissions,
            "is_active": new_admin.is_active,
            "created_at": new_admin.created_at,
            "updated_at": new_admin.updated_at
        }
    
    def update_admin_user(
        self,
        admin_id: int,
        update_data: Dict,
        current_admin: AdminUser
    ) -> Dict:
        """Update admin user with specified data"""
        # Verify current admin is super_admin
        if current_admin.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super_admin can update admin users"
            )
        
        # Get admin user to update
        admin_to_update = self.db.query(AdminUser).filter(
            AdminUser.admin_id == admin_id
        ).first()
        
        if not admin_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin user not found"
            )
        
        # Store old values for audit log
        old_value = {
            "email": admin_to_update.email,
            "full_name": admin_to_update.full_name,
            "role": admin_to_update.role,
            "permissions": admin_to_update.permissions,
            "is_active": admin_to_update.is_active
        }
        
        # Update role if provided
        if "role" in update_data:
            if update_data["role"] not in ["admin", "super_admin"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role must be either 'admin' or 'super_admin'"
                )
            admin_to_update.role = update_data["role"]
        
        # Update permissions if provided
        if "permissions" in update_data:
            if not isinstance(update_data["permissions"], list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Permissions must be a list"
                )
            admin_to_update.permissions = update_data["permissions"]
        
        # Update full_name if provided
        if "full_name" in update_data:
            admin_to_update.full_name = update_data["full_name"]
        
        admin_to_update.updated_at = datetime.utcnow()
        
        # Create audit log entry
        audit_log = AuditLog(
            admin_id=current_admin.admin_id,
            action="update_admin",
            resource_type="admin_user",
            resource_id=admin_id,
            old_value=old_value,
            new_value={
                "email": admin_to_update.email,
                "full_name": admin_to_update.full_name,
                "role": admin_to_update.role,
                "permissions": admin_to_update.permissions,
                "is_active": admin_to_update.is_active
            },
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return {
            "admin_id": admin_to_update.admin_id,
            "email": admin_to_update.email,
            "full_name": admin_to_update.full_name,
            "role": admin_to_update.role,
            "permissions": admin_to_update.permissions,
            "is_active": admin_to_update.is_active,
            "created_at": admin_to_update.created_at,
            "updated_at": admin_to_update.updated_at
        }
    
    def deactivate_admin_user(
        self,
        admin_id: int,
        current_admin: AdminUser
    ) -> Dict:
        """Deactivate admin user"""
        # Verify current admin is super_admin
        if current_admin.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super_admin can deactivate admin users"
            )
        
        # Get admin user to deactivate
        admin_to_deactivate = self.db.query(AdminUser).filter(
            AdminUser.admin_id == admin_id
        ).first()
        
        if not admin_to_deactivate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin user not found"
            )
        
        # Store old value for audit log
        old_value = {
            "is_active": admin_to_deactivate.is_active
        }
        
        # Deactivate admin user
        admin_to_deactivate.is_active = False
        admin_to_deactivate.updated_at = datetime.utcnow()
        
        # Create audit log entry
        audit_log = AuditLog(
            admin_id=current_admin.admin_id,
            action="delete_admin",
            resource_type="admin_user",
            resource_id=admin_id,
            old_value=old_value,
            new_value={"is_active": False},
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return {
            "admin_id": admin_to_deactivate.admin_id,
            "email": admin_to_deactivate.email,
            "full_name": admin_to_deactivate.full_name,
            "role": admin_to_deactivate.role,
            "permissions": admin_to_deactivate.permissions,
            "is_active": admin_to_deactivate.is_active,
            "created_at": admin_to_deactivate.created_at,
            "updated_at": admin_to_deactivate.updated_at
        }
    
    def list_admin_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """List all admin users with pagination"""
        admin_users = self.db.query(AdminUser).offset(skip).limit(limit).all()
        
        return [
            {
                "admin_id": admin.admin_id,
                "email": admin.email,
                "full_name": admin.full_name,
                "role": admin.role,
                "permissions": admin.permissions,
                "is_active": admin.is_active,
                "created_at": admin.created_at,
                "updated_at": admin.updated_at
            }
            for admin in admin_users
        ]
    
    def get_admin_user(self, admin_id: int) -> Dict:
        """Get specific admin user by ID"""
        admin = self.db.query(AdminUser).filter(
            AdminUser.admin_id == admin_id
        ).first()
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin user not found"
            )
        
        return {
            "admin_id": admin.admin_id,
            "email": admin.email,
            "full_name": admin.full_name,
            "role": admin.role,
            "permissions": admin.permissions,
            "is_active": admin.is_active,
            "created_at": admin.created_at,
            "updated_at": admin.updated_at
        }

    def _check_data_consistency(self, app) -> list:
        """Check for suspicious/inconsistent data patterns"""
        flags = []
        alt = app.alternative_data or {}
        income = alt.get('monthly_income', 0) or 0
        expenses = alt.get('monthly_expenses', 0) or 0
        age = app.age or 25
        stability = alt.get('employment_stability_years', 0) or 0
        gig_rating = alt.get('gig_platform_rating', 0) or 0
        upi_freq = alt.get('upi_transaction_frequency', 0) or 0
        savings = alt.get('savings_account_balance', 0) or 0
        repayment_score = alt.get('loan_repayment_history_score', 5) or 5
        existing_loans = alt.get('existing_loan_count', 0) or 0
        microfinance = alt.get('microfinance_repayment_count', 0) or 0
        community_score = alt.get('community_verification_score', 5) or 5

        # Income vs loan amount
        if income > 0 and app.requested_amount > income * 24:
            flags.append("⚠️ Loan amount exceeds 24x monthly income — unusually high")

        # Expenses > income
        if expenses > 0 and income > 0 and expenses >= income:
            flags.append("⚠️ Monthly expenses ≥ monthly income — no disposable income")

        # Age vs employment stability
        if age < 22 and stability > 5:
            flags.append(f"⚠️ Age {age} but claims {stability} years employment — inconsistent")

        # Perfect scores
        if gig_rating == 5.0 and upi_freq < 5:
            flags.append("⚠️ Perfect gig rating (5.0) but very low UPI activity — suspicious")

        if repayment_score == 10 and existing_loans == 0 and microfinance == 0:
            flags.append("⚠️ Perfect repayment score (10) but no loan history — unverifiable")

        if community_score == 10 and microfinance == 0:
            flags.append("⚠️ Perfect community score (10) but no microfinance history — unverifiable")

        # Very high income with no savings
        if income > 50000 and savings < 1000:
            flags.append("⚠️ High income (₹{:,}) but near-zero savings — inconsistent".format(int(income)))

        # Extremely low expenses
        if income > 0 and expenses > 0 and expenses < income * 0.1:
            flags.append("⚠️ Expenses are less than 10% of income — likely underreported")

        return flags

    def list_all_applications(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> List[Dict]:
        """List all applications with optional filtering by status"""
        query = self.db.query(Application)
        
        if status_filter:
            query = query.filter(Application.status == status_filter)
        
        applications = query.offset(skip).limit(limit).all()
        
        return [
            {
                "application_id": app.id,
                "user_id": app.user_id,
                "applicant_type": app.applicant_type,
                "full_name": app.full_name,
                "age": app.age,
                "phone_number": app.phone_number,
                "address": app.address,
                "requested_amount": app.requested_amount,
                "loan_purpose": app.loan_purpose,
                "alternative_data": app.alternative_data,
                "status": app.status,
                "credit_score": app.credit_score.credit_score if app.credit_score else None,
                "risk_category": app.credit_score.risk_category if app.credit_score else None,
                "document_links": app.document_links or {},
                "consistency_flags": self._check_data_consistency(app),
                "created_at": app.created_at,
                "updated_at": app.updated_at
            }
            for app in applications
        ]
    
    def get_application_details(self, application_id: int) -> Dict:
        """Get application details by ID"""
        application = self.db.query(Application).filter(
            Application.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        return {
            "application_id": application.id,
            "user_id": application.user_id,
            "applicant_type": application.applicant_type,
            "full_name": application.full_name,
            "age": application.age,
            "phone_number": application.phone_number,
            "address": application.address,
            "requested_amount": application.requested_amount,
            "loan_purpose": application.loan_purpose,
            "alternative_data": application.alternative_data,
            "status": application.status,
            "credit_score": application.credit_score.credit_score if application.credit_score else None,
            "risk_category": application.credit_score.risk_category if application.credit_score else None,
            "document_links": application.document_links or {},
            "consistency_flags": self._check_data_consistency(application),
            "created_at": application.created_at,
            "updated_at": application.updated_at
        }
    
    def update_application_status(
        self,
        application_id: int,
        status_update,
        admin_id: int
    ) -> Dict:
        """Update application status with validation and audit logging"""
        # Verify admin exists and is active
        admin = self.db.query(AdminUser).filter(
            AdminUser.admin_id == admin_id
        ).first()
        
        if not admin or not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin user not found or inactive"
            )
        
        # Check if admin has approve_application permission (super_admin bypasses)
        if admin.role != "super_admin" and "approve_application" not in admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin does not have permission to approve applications"
            )
        
        # Query application from database
        application = self.db.query(Application).filter(
            Application.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Validate status value
        valid_statuses = ["pending", "approved", "rejected", "under_review"]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Validate status transition
        valid_transitions = {
            "pending": ["approved", "rejected", "under_review"],
            "under_review": ["approved", "rejected"],
            "approved": [],
            "rejected": []
        }
        
        if status_update.status not in valid_transitions.get(application.status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from '{application.status}' to '{status_update.status}'"
            )
        
        # Store old value for audit log
        old_value = {"status": application.status}
        
        # Update application status
        application.status = status_update.status
        application.updated_at = datetime.utcnow()
        
        # Create audit log entry
        audit_log = AuditLog(
            admin_id=admin_id,
            action="update_status",
            resource_type="application",
            resource_id=application_id,
            old_value=old_value,
            new_value={"status": status_update.status},
            timestamp=datetime.utcnow()
        )
        
        # Add notes and reason to audit log if provided
        if status_update.notes or status_update.reason:
            audit_log.new_value["notes"] = status_update.notes
            audit_log.new_value["reason"] = status_update.reason
        
        self.db.add(audit_log)
        self.db.commit()
        
        # Send email notification to applicant if approved or rejected
        if status_update.status in ["approved", "rejected"]:
            try:
                applicant = self.db.query(User).filter(User.id == application.user_id).first()
                if applicant:
                    email_service = EmailService()
                    email_service.send_status_notification(
                        to_email=applicant.email,
                        full_name=applicant.full_name,
                        application_id=application_id,
                        new_status=status_update.status,
                        reason=status_update.notes or status_update.reason
                    )
            except Exception as e:
                print(f"Warning: Failed to send status notification email: {e}")
        
        # Invalidate analytics cache
        self._invalidate_analytics_cache()
        
        return {
            "application_id": application.id,
            "user_id": application.user_id,
            "applicant_type": application.applicant_type,
            "full_name": application.full_name,
            "age": application.age,
            "phone_number": application.phone_number,
            "address": application.address,
            "requested_amount": application.requested_amount,
            "loan_purpose": application.loan_purpose,
            "alternative_data": application.alternative_data,
            "status": application.status,
            "credit_score": application.credit_score.credit_score if application.credit_score else None,
            "risk_category": application.credit_score.risk_category if application.credit_score else None,
            "created_at": application.created_at,
            "updated_at": application.updated_at
        }
    
    def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        admin_id: Optional[int] = None,
        action: Optional[str] = None
    ) -> List[Dict]:
        """Get audit logs with optional filtering"""
        query = self.db.query(AuditLog)
        
        if admin_id:
            query = query.filter(AuditLog.admin_id == admin_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        audit_logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "admin_id": log.admin_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "timestamp": log.timestamp
            }
            for log in audit_logs
        ]
    
    def _invalidate_analytics_cache(self):
        """Invalidate analytics cache"""
        # This is a placeholder for cache invalidation logic
        # In a real implementation, this would interact with Redis or similar
        pass
