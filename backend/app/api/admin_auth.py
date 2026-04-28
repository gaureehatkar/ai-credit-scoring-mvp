from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.admin import AdminLogin, AdminTokenResponse, AdminUserResponse
from app.services.admin_auth_service import AdminAuthService
from app.utils.dependencies import get_current_admin_user
from app.models.admin_user import AdminUser

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint - authenticate with email and password"""
    auth_service = AdminAuthService(db)
    return auth_service.authenticate_admin(credentials)


@router.post("/logout")
async def admin_logout(current_admin: AdminUser = Depends(get_current_admin_user)):
    """Admin logout endpoint (optional - JWT tokens are stateless)"""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AdminUserResponse)
async def get_current_admin_info(current_admin: AdminUser = Depends(get_current_admin_user)):
    """Get current admin info"""
    return current_admin
