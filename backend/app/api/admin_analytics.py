from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database import get_db
from app.schemas.analytics import DashboardMetrics
from app.services.analytics_service import AnalyticsService
from app.utils.dependencies import get_current_admin_user as get_current_admin
from app.models.admin_user import AdminUser

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    days: int = Query(30, ge=1, le=365),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics for specified period"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_dashboard_metrics(days)


@router.get("/credit-score-distribution", response_model=List[Dict])
async def get_credit_score_distribution(
    days: int = Query(30, ge=1, le=365),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get credit score distribution for specified period"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_credit_score_distribution(days)


@router.get("/risk-distribution", response_model=Dict)
async def get_risk_distribution(
    days: int = Query(30, ge=1, le=365),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get risk distribution for specified period"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_risk_distribution(days)


@router.post("/cache/invalidate")
async def invalidate_cache(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Invalidate analytics cache"""
    analytics_service = AnalyticsService(db)
    analytics_service.invalidate_cache()
    return {"message": "Analytics cache invalidated successfully"}
