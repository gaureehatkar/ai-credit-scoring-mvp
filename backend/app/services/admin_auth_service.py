from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from app.models.admin_user import AdminUser
from app.schemas.admin import AdminLogin, AdminTokenResponse, AdminUserCreate
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.security import decode_access_token


class AdminAuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_admin(self, credentials: AdminLogin) -> AdminTokenResponse:
        """Authenticate admin user and return JWT token with admin scope"""
        admin = self.db.query(AdminUser).filter(AdminUser.email == credentials.email).first()
        
        if not admin or not verify_password(credentials.password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify admin has admin or super_admin role
        if admin.role not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not have admin role"
            )
        
        # Verify admin is active
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin account is inactive"
            )
        
        # Generate JWT token with admin scope
        access_token = create_access_token(
            data={
                "sub": str(admin.admin_id),
                "email": admin.email,
                "role": admin.role,
                "permissions": admin.permissions,
                "scope": "admin"
            }
        )
        
        return AdminTokenResponse(
            access_token=access_token,
            token_type="bearer",
            admin_id=admin.admin_id,
            email=admin.email,
            role=admin.role,
            permissions=admin.permissions
        )
    
    def verify_admin_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and validate admin role"""
        payload = decode_access_token(token)
        
        if payload is None:
            return None
        
        # Check if token has admin scope
        if payload.get("scope") != "admin":
            return None
        
        # Verify admin still exists and is active
        admin_id = payload.get("sub")
        if admin_id is None:
            return None
        
        admin = self.db.query(AdminUser).filter(AdminUser.admin_id == int(admin_id)).first()
        if not admin or not admin.is_active:
            return None
        
        return payload
    
    def check_permission(self, admin_id: int, permission: str) -> bool:
        """Check if admin has specific permission"""
        admin = self.db.query(AdminUser).filter(AdminUser.admin_id == admin_id).first()
        
        if not admin or not admin.is_active:
            return False
        
        # Super admin has all permissions
        if admin.role == "super_admin":
            return True
        
        # Check if permission is in admin's permissions list
        return permission in admin.permissions
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return hash_password(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return verify_password(plain_password, hashed_password)
