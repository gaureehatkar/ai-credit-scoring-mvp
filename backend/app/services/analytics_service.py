from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from app.models.application import Application
from app.models.credit_score import CreditScore
from app.schemas.analytics import DashboardMetrics


class AnalyticsCache:
    """Simple in-memory cache for analytics data"""
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # (data, expiry_time)
    
    def get(self, key: str) -> Optional[dict]:
        """Get cached value if not expired"""
        if key in self._cache:
            data, expiry_time = self._cache[key]
            if datetime.utcnow() < expiry_time:
                return data
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: dict, ttl_seconds: int = 300):
        """Set cache value with TTL"""
        expiry_time = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expiry_time)
    
    def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries matching pattern or all if pattern is None"""
        if pattern is None:
            self._cache.clear()
        else:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]


# Global cache instance
_analytics_cache = AnalyticsCache()


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = _analytics_cache
        self.cache_ttl = 300  # 5 minutes
    
    def get_dashboard_metrics(self, days: int = 30) -> DashboardMetrics:
        """Get aggregated dashboard metrics for specified period"""
        # Validate days parameter
        if days < 1 or days > 365:
            raise ValueError("Days must be between 1 and 365")
        
        # Check cache first
        cache_key = f"analytics:dashboard:{days}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return DashboardMetrics(**cached_result)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query applications in date range
        applications = self.db.query(Application).filter(
            Application.created_at >= start_date,
            Application.created_at <= end_date
        ).all()
        
        # Count applications by status
        status_counts = {
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "under_review": 0
        }
        
        for app in applications:
            if app.status in status_counts:
                status_counts[app.status] += 1
        
        # Calculate total and approval rate
        total_apps = len(applications)
        approval_rate = (status_counts["approved"] / total_apps * 100) if total_apps > 0 else 0.0
        
        # Query credit scores for distribution
        credit_scores = self.db.query(CreditScore).join(Application).filter(
            Application.created_at >= start_date,
            Application.created_at <= end_date
        ).all()
        
        # Calculate average credit score
        if credit_scores:
            average_score = sum(cs.credit_score for cs in credit_scores) / len(credit_scores)
        else:
            average_score = 0.0
        
        # Compute risk category metrics
        risk_distribution = {
            "low": sum(1 for cs in credit_scores if cs.risk_category == "low"),
            "medium": sum(1 for cs in credit_scores if cs.risk_category == "medium"),
            "high": sum(1 for cs in credit_scores if cs.risk_category == "high")
        }
        
        # Create metrics object
        metrics = DashboardMetrics(
            timestamp=datetime.utcnow(),
            total_applications=total_apps,
            approval_rate=approval_rate,
            average_credit_score=average_score,
            risk_distribution=risk_distribution
        )
        
        # Cache the result
        self.cache.set(cache_key, metrics.model_dump(), self.cache_ttl)
        
        return metrics
    
    def get_credit_score_distribution(self, days: int = 30) -> List[Dict]:
        """Get credit score distribution across ranges"""
        # Validate days parameter
        if days < 1 or days > 365:
            raise ValueError("Days must be between 1 and 365")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query credit scores for distribution
        credit_scores = self.db.query(CreditScore).join(Application).filter(
            Application.created_at >= start_date,
            Application.created_at <= end_date
        ).all()
        
        # Define score ranges
        score_ranges = [(300, 400), (400, 500), (500, 600), (600, 700), (700, 800), (800, 850)]
        score_distribution = []
        
        for min_score, max_score in score_ranges:
            count = sum(1 for cs in credit_scores if min_score <= cs.credit_score < max_score)
            score_distribution.append({
                "range": f"{min_score}-{max_score}",
                "count": count
            })
        
        return score_distribution
    
    def get_risk_distribution(self, days: int = 30) -> Dict:
        """Get risk distribution for specified period"""
        # Validate days parameter
        if days < 1 or days > 365:
            raise ValueError("Days must be between 1 and 365")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query credit scores for risk distribution
        credit_scores = self.db.query(CreditScore).join(Application).filter(
            Application.created_at >= start_date,
            Application.created_at <= end_date
        ).all()
        
        # Compute risk category metrics
        risk_distribution = {
            "low": sum(1 for cs in credit_scores if cs.risk_category == "low"),
            "medium": sum(1 for cs in credit_scores if cs.risk_category == "medium"),
            "high": sum(1 for cs in credit_scores if cs.risk_category == "high")
        }
        
        return risk_distribution
    
    def invalidate_cache(self) -> None:
        """Invalidate all analytics cache"""
        self.cache.invalidate(pattern="analytics:")
