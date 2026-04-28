from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_id: int
    email: str
    role: str
    permissions: List[str]


class AdminUserResponse(BaseModel):
    admin_id: int
    email: str
    full_name: str
    role: str
    permissions: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    role: str = "admin"
    permissions: List[str] = []


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
