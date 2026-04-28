from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List


class CreditScoreDistribution(BaseModel):
    range: str
    count: int


class RiskDistribution(BaseModel):
    category: str
    count: int


class DashboardMetrics(BaseModel):
    timestamp: datetime
    total_applications: int
    approval_rate: float
    average_credit_score: float
    risk_distribution: Dict[str, int]
    
    class Config:
        from_attributes = True
