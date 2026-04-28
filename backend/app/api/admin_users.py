from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.admin import AdminUserCreate, AdminUserResponse, AdminUserUpdate
from app.services.admin_service import AdminService
from app.utils.dependencies import get_current_admin_user, require_permission

router = APIRouter(prefix="/admin/users", tags=["admin_users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AdminUserResponse)
async def create_admin_user(
    admin_data: AdminUserCreate,
    current_admin: AdminUser = Depends(require_permission("create_admin")),
    db: Session = Depends(get_db)
):
    """Create new admin user (super_admin only)"""
    admin_service = AdminService(db)
    result = admin_service.create_admin_user(admin_data, current_admin)
    return result


@router.get("", response_model=List[AdminUserResponse])
async def list_admin_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all admin users"""
    admin_service = AdminService(db)
    return admin_service.list_admin_users(skip, limit)


@router.get("/{admin_id}", response_model=AdminUserResponse)
async def get_admin_user(
    admin_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get specific admin user"""
    admin_service = AdminService(db)
    return admin_service.get_admin_user(admin_id)


@router.patch("/{admin_id}", response_model=AdminUserResponse)
async def update_admin_user(
    admin_id: int,
    update_data: AdminUserUpdate,
    current_admin: AdminUser = Depends(require_permission("update_admin")),
    db: Session = Depends(get_db)
):
    """Update admin user (super_admin only)"""
    admin_service = AdminService(db)
    # Convert Pydantic model to dict, excluding None values
    update_dict = update_data.model_dump(exclude_none=True)
    return admin_service.update_admin_user(admin_id, update_dict, current_admin)


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_admin_user(
    admin_id: int,
    current_admin: AdminUser = Depends(require_permission("delete_admin")),
    db: Session = Depends(get_db)
):
    """Deactivate admin user (super_admin only)"""
    admin_service = AdminService(db)
    admin_service.deactivate_admin_user(admin_id, current_admin)
    return None
