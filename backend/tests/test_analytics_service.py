import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.application import Application
from app.models.credit_score import CreditScore
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def db():
    """Create test database and session"""
    # Use in-memory database for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def sample_data(db):
    """Create sample data for testing"""
    # Create users
    user1 = User(email="user1@test.com", hashed_password="hashed", full_name="User 1")
    user2 = User(email="user2@test.com", hashed_password="hashed", full_name="User 2")
    user3 = User(email="user3@test.com", hashed_password="hashed", full_name="User 3")
    db.add_all([user1, user2, user3])
    db.commit()
    
    # Create applications with different statuses
    now = datetime.utcnow()
    app1 = Application(
        user_id=user1.id,
        applicant_type="individual",
        full_name="User 1",
        age=30,
        phone_number="1234567890",
        address="123 Main St",
        requested_amount=10000.0,
        loan_purpose="business",
        alternative_data={},
        status="approved",
        created_at=now - timedelta(days=10)
    )
    app2 = Application(
        user_id=user2.id,
        applicant_type="individual",
        full_name="User 2",
        age=25,
        phone_number="0987654321",
        address="456 Oak Ave",
        requested_amount=5000.0,
        loan_purpose="personal",
        alternative_data={},
        status="rejected",
        created_at=now - timedelta(days=5)
    )
    app3 = Application(
        user_id=user3.id,
        applicant_type="individual",
        full_name="User 3",
        age=35,
        phone_number="5555555555",
        address="789 Pine Rd",
        requested_amount=15000.0,
        loan_purpose="education",
        alternative_data={},
        status="pending",
        created_at=now - timedelta(days=2)
    )
    db.add_all([app1, app2, app3])
    db.commit()
    
    # Create credit scores
    score1 = CreditScore(
        application_id=app1.id,
        credit_score=750.0,
        default_probability=0.1,
        risk_category="low",
        shap_explanations={},
        model_version="v1.0"
    )
    score2 = CreditScore(
        application_id=app2.id,
        credit_score=450.0,
        default_probability=0.8,
        risk_category="high",
        shap_explanations={},
        model_version="v1.0"
    )
    score3 = CreditScore(
        application_id=app3.id,
        credit_score=600.0,
        default_probability=0.4,
        risk_category="medium",
        shap_explanations={},
        model_version="v1.0"
    )
    db.add_all([score1, score2, score3])
    db.commit()
    
    return {
        "users": [user1, user2, user3],
        "applications": [app1, app2, app3],
        "scores": [score1, score2, score3]
    }


def test_get_dashboard_metrics(db, sample_data):
    """Test dashboard metrics calculation"""
    service = AnalyticsService(db)
    metrics = service.get_dashboard_metrics(days=30)
    
    assert metrics.total_applications == 3
    assert metrics.approval_rate == pytest.approx(33.33, rel=0.1)
    assert metrics.average_credit_score == pytest.approx(600.0, rel=0.1)
    assert metrics.risk_distribution["low"] == 1
    assert metrics.risk_distribution["medium"] == 1
    assert metrics.risk_distribution["high"] == 1


def test_get_credit_score_distribution(db, sample_data):
    """Test credit score distribution calculation"""
    service = AnalyticsService(db)
    distribution = service.get_credit_score_distribution(days=30)
    
    assert len(distribution) == 6
    
    # Check that scores are in correct ranges
    ranges = {item["range"]: item["count"] for item in distribution}
    assert ranges["400-500"] == 1  # score 450
    assert ranges["600-700"] == 1  # score 600
    assert ranges["700-800"] == 1  # score 750


def test_get_risk_distribution(db, sample_data):
    """Test risk distribution calculation"""
    service = AnalyticsService(db)
    risk_dist = service.get_risk_distribution(days=30)
    
    assert risk_dist["low"] == 1
    assert risk_dist["medium"] == 1
    assert risk_dist["high"] == 1


def test_cache_functionality(db, sample_data):
    """Test analytics caching"""
    service = AnalyticsService(db)
    
    # First call should compute and cache
    metrics1 = service.get_dashboard_metrics(days=30)
    
    # Second call should return cached result
    metrics2 = service.get_dashboard_metrics(days=30)
    
    assert metrics1.timestamp == metrics2.timestamp
    
    # Invalidate cache
    service.invalidate_cache()
    
    # Next call should recompute
    metrics3 = service.get_dashboard_metrics(days=30)
    assert metrics3.timestamp >= metrics2.timestamp


def test_invalid_days_parameter(db):
    """Test validation of days parameter"""
    service = AnalyticsService(db)
    
    with pytest.raises(ValueError):
        service.get_dashboard_metrics(days=0)
    
    with pytest.raises(ValueError):
        service.get_dashboard_metrics(days=400)


def test_empty_database(db):
    """Test analytics with no data"""
    service = AnalyticsService(db)
    # Clear cache to ensure fresh test
    service.invalidate_cache()
    
    metrics = service.get_dashboard_metrics(days=30)
    
    assert metrics.total_applications == 0
    assert metrics.approval_rate == 0.0
    assert metrics.average_credit_score == 0.0
    assert metrics.risk_distribution["low"] == 0
    assert metrics.risk_distribution["medium"] == 0
    assert metrics.risk_distribution["high"] == 0
