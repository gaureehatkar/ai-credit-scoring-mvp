# Design Document: AI-Powered Credit Scoring MVP Platform

## Overview

This design describes a minimal viable product (MVP) for an AI-powered credit scoring platform targeting unbanked and underbanked populations. The platform uses machine learning to evaluate creditworthiness based on alternative data sources, providing financial inclusion for individuals and MSMEs lacking traditional credit histories. The MVP follows a simple 3-tier architecture with a FastAPI backend, React/TypeScript frontend, PostgreSQL database, and pre-trained ML models with SHAP explainability. The system is designed for a semester EDI project with focus on essential features: credit application submission, ML-based scoring, and transparent explanations.

## Architecture

The MVP uses a monolithic 3-tier architecture optimized for rapid development and deployment within a semester timeframe.

```mermaid
graph TB
    subgraph "Client Layer"
        UI[React Frontend<br/>TypeScript]
    end
    
    subgraph "Application Layer"
        API[FastAPI Backend<br/>Python 3.10+]
        AUTH[JWT Authentication]
        CREDIT[Credit Service]
        PREDICT[Prediction Service]
        SHAP[SHAP Explainer]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Database)]
        MODEL[Pre-trained ML Models<br/>XGBoost + scikit-learn]
    end
    
    UI -->|REST API| API
    API --> AUTH
    API --> CREDIT
    API --> PREDICT
    PREDICT --> SHAP
    PREDICT --> MODEL
    CREDIT --> DB
    AUTH --> DB
```

## Sequence Diagrams

### Credit Application Submission and Scoring Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AuthService
    participant CreditService
    participant PredictionService
    participant SHAPExplainer
    participant Database
    participant MLModel
    
    User->>Frontend: Fill credit application form
    Frontend->>API: POST /api/v1/applications (with JWT)
    API->>AuthService: Validate JWT token
    AuthService-->>API: User authenticated
    
    API->>CreditService: Create application
    CreditService->>Database: INSERT application record
    Database-->>CreditService: Application ID
    
    CreditService->>PredictionService: Request credit score
    PredictionService->>PredictionService: Extract & engineer features
    PredictionService->>MLModel: Predict credit score
    MLModel-->>PredictionService: Score + probability
    
    PredictionService->>SHAPExplainer: Generate explanation
    SHAPExplainer-->>PredictionService: SHAP values
    
    PredictionService->>Database: INSERT credit_score record
    Database-->>PredictionService: Score ID
    
    PredictionService-->>CreditService: Score + explanation
    CreditService-->>API: Application result
    API-->>Frontend: Credit score response
    Frontend-->>User: Display score + explanation
```


### User Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AuthService
    participant Database
    
    User->>Frontend: Enter credentials
    Frontend->>API: POST /api/v1/auth/login
    API->>AuthService: Authenticate user
    AuthService->>Database: Query user by email
    Database-->>AuthService: User record
    AuthService->>AuthService: Verify password hash
    AuthService->>AuthService: Generate JWT token
    AuthService-->>API: JWT token + user info
    API-->>Frontend: Authentication response
    Frontend->>Frontend: Store JWT in localStorage
    Frontend-->>User: Redirect to dashboard
```

## Components and Interfaces

### Component 1: Authentication Service

**Purpose**: Handles user registration, login, and JWT token management for secure API access.

**Interface**:
```python
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "applicant"  # applicant or admin

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: str

class AuthService:
    def register_user(self, user_data: UserCreate) -> TokenResponse:
        """Register new user and return JWT token"""
        pass
    
    def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
        """Authenticate user and return JWT token"""
        pass
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return user payload"""
        pass
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        pass
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        pass
```

**Responsibilities**:
- User registration with password hashing (bcrypt)
- User authentication with email/password
- JWT token generation and validation
- Role-based access control (applicant vs admin)


### Component 2: Credit Service

**Purpose**: Manages credit application lifecycle including creation, retrieval, and status updates.

**Interface**:
```python
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ApplicantType(str, Enum):
    UNBANKED = "unbanked"
    UNDERBANKED = "underbanked"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

class AlternativeDataInput(BaseModel):
    # Common fields
    monthly_income: Optional[float] = Field(None, ge=0)
    utility_payment_history: Optional[str] = None  # JSON string
    employment_type: Optional[str] = None
    
    # Unbanked specific
    remittance_frequency: Optional[int] = Field(None, ge=0)
    community_verification_score: Optional[float] = Field(None, ge=0, le=10)
    microfinance_repayment_count: Optional[int] = Field(None, ge=0)
    
    # Underbanked specific
    gig_platform_rating: Optional[float] = Field(None, ge=0, le=5)
    upi_transaction_frequency: Optional[int] = Field(None, ge=0)
    savings_account_balance: Optional[float] = Field(None, ge=0)

class CreditApplicationCreate(BaseModel):
    applicant_type: ApplicantType
    full_name: str
    age: int = Field(..., ge=18, le=100)
    phone_number: str
    address: str
    requested_amount: float = Field(..., gt=0)
    loan_purpose: str
    alternative_data: AlternativeDataInput

class CreditApplicationResponse(BaseModel):
    application_id: int
    user_id: int
    applicant_type: ApplicantType
    status: ApplicationStatus
    requested_amount: float
    credit_score: Optional[float] = None
    risk_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CreditService:
    def create_application(
        self, 
        user_id: int, 
        application_data: CreditApplicationCreate
    ) -> CreditApplicationResponse:
        """Create new credit application and trigger scoring"""
        pass
    
    def get_application(self, application_id: int, user_id: int) -> CreditApplicationResponse:
        """Retrieve application by ID with authorization check"""
        pass
    
    def list_user_applications(self, user_id: int) -> List[CreditApplicationResponse]:
        """List all applications for a user"""
        pass
    
    def list_all_applications(self, skip: int = 0, limit: int = 100) -> List[CreditApplicationResponse]:
        """List all applications (admin only)"""
        pass
    
    def update_application_status(
        self, 
        application_id: int, 
        status: ApplicationStatus
    ) -> CreditApplicationResponse:
        """Update application status (admin only)"""
        pass
```

**Responsibilities**:
- Create and validate credit applications
- Store application data in database
- Coordinate with prediction service for scoring
- Manage application status lifecycle
- Provide application retrieval with proper authorization


### Component 3: Prediction Service

**Purpose**: Performs ML-based credit scoring using pre-trained models and generates SHAP explanations for transparency.

**Interface**:
```python
from typing import Dict, List, Tuple
import numpy as np
from pydantic import BaseModel

class FeatureVector(BaseModel):
    features: Dict[str, float]
    feature_names: List[str]

class SHAPExplanation(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float
    impact: str  # "positive" or "negative"

class CreditScoreResult(BaseModel):
    credit_score: float  # 300-850 scale
    default_probability: float  # 0-1
    risk_category: str  # "low", "medium", "high"
    shap_explanations: List[SHAPExplanation]
    model_version: str

class PredictionService:
    def __init__(self, model_path: str):
        """Initialize with pre-trained model"""
        pass
    
    def engineer_features(
        self, 
        application_data: CreditApplicationCreate
    ) -> FeatureVector:
        """
        Extract and engineer features from application data.
        Handles missing values and creates derived features.
        """
        pass
    
    def predict_credit_score(
        self, 
        features: FeatureVector
    ) -> CreditScoreResult:
        """
        Predict credit score and generate SHAP explanations.
        Returns score on 300-850 scale with risk category.
        """
        pass
    
    def calculate_risk_category(self, credit_score: float) -> str:
        """
        Categorize risk based on credit score:
        - low: 700-850
        - medium: 600-699
        - high: 300-599
        """
        pass
    
    def generate_shap_explanation(
        self, 
        features: FeatureVector, 
        prediction: float
    ) -> List[SHAPExplanation]:
        """Generate SHAP values for model transparency"""
        pass
    
    def load_model(self, model_path: str) -> None:
        """Load pre-trained XGBoost model from disk"""
        pass
```

**Responsibilities**:
- Feature engineering from raw application data
- Credit score prediction using XGBoost model
- SHAP value computation for explainability
- Risk categorization based on score thresholds
- Model loading and version management


### Component 4: Database Layer

**Purpose**: Persistent storage for users, applications, and credit scores using PostgreSQL with SQLAlchemy ORM.

**Interface**:
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="applicant")  # applicant or admin
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applications = relationship("Application", back_populates="user")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    applicant_type = Column(String, nullable=False)  # unbanked or underbanked
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(String, nullable=False)
    requested_amount = Column(Float, nullable=False)
    loan_purpose = Column(String, nullable=False)
    alternative_data = Column(JSON, nullable=False)  # Stores AlternativeDataInput as JSON
    status = Column(String, default="pending")  # pending, approved, rejected, under_review
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="applications")
    credit_score = relationship("CreditScore", back_populates="application", uselist=False)

class CreditScore(Base):
    __tablename__ = "credit_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False)
    credit_score = Column(Float, nullable=False)  # 300-850 scale
    default_probability = Column(Float, nullable=False)  # 0-1
    risk_category = Column(String, nullable=False)  # low, medium, high
    shap_explanations = Column(JSON, nullable=False)  # List of SHAP values
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    application = relationship("Application", back_populates="credit_score")

class DatabaseService:
    def __init__(self, database_url: str):
        """Initialize database connection"""
        pass
    
    def create_tables(self) -> None:
        """Create all tables if they don't exist"""
        pass
    
    def get_session(self):
        """Get database session for transactions"""
        pass
```

**Responsibilities**:
- Define database schema with proper relationships
- Manage database connections and sessions
- Provide ORM models for type-safe queries
- Handle database migrations (using Alembic)


## Data Models

### Model 1: User

```python
class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str  # "applicant" or "admin"
    created_at: datetime
    updated_at: datetime
```

**Validation Rules**:
- Email must be valid format and unique
- Role must be either "applicant" or "admin"
- Password must be at least 8 characters (enforced at creation)
- Full name must not be empty

### Model 2: Application

```python
class Application(BaseModel):
    id: int
    user_id: int
    applicant_type: ApplicantType  # "unbanked" or "underbanked"
    full_name: str
    age: int  # 18-100
    phone_number: str
    address: str
    requested_amount: float  # > 0
    loan_purpose: str
    alternative_data: AlternativeDataInput
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
```

**Validation Rules**:
- Age must be between 18 and 100
- Requested amount must be positive
- Phone number must match valid format
- Alternative data fields validated based on applicant_type
- Status transitions: pending → approved/rejected/under_review

### Model 3: CreditScore

```python
class CreditScore(BaseModel):
    id: int
    application_id: int
    credit_score: float  # 300-850
    default_probability: float  # 0-1
    risk_category: str  # "low", "medium", "high"
    shap_explanations: List[SHAPExplanation]
    model_version: str
    created_at: datetime
```

**Validation Rules**:
- Credit score must be between 300 and 850
- Default probability must be between 0 and 1
- Risk category must be "low", "medium", or "high"
- SHAP explanations must contain at least top 5 features
- One-to-one relationship with Application

### Model 4: AlternativeDataInput

```python
class AlternativeDataInput(BaseModel):
    # Common fields
    monthly_income: Optional[float] = None  # >= 0
    utility_payment_history: Optional[str] = None
    employment_type: Optional[str] = None
    
    # Unbanked specific
    remittance_frequency: Optional[int] = None  # >= 0
    community_verification_score: Optional[float] = None  # 0-10
    microfinance_repayment_count: Optional[int] = None  # >= 0
    
    # Underbanked specific
    gig_platform_rating: Optional[float] = None  # 0-5
    upi_transaction_frequency: Optional[int] = None  # >= 0
    savings_account_balance: Optional[float] = None  # >= 0
```

**Validation Rules**:
- All numeric fields must be non-negative where specified
- Ratings must be within valid ranges (0-5, 0-10)
- At least 3 alternative data fields must be provided
- Field requirements vary by applicant_type


## Algorithmic Pseudocode

### Main Processing Algorithm: Credit Application Scoring

```python
def process_credit_application(application_data: CreditApplicationCreate, user_id: int) -> CreditApplicationResponse:
    """
    Main algorithm for processing credit application and generating score.
    
    INPUT: application_data (validated application form), user_id (authenticated user)
    OUTPUT: CreditApplicationResponse with score and explanations
    """
    # Preconditions
    assert application_data is not None
    assert user_id > 0
    assert application_data.age >= 18
    assert application_data.requested_amount > 0
    
    # Step 1: Create application record in database
    application = db.create_application(
        user_id=user_id,
        applicant_type=application_data.applicant_type,
        full_name=application_data.full_name,
        age=application_data.age,
        phone_number=application_data.phone_number,
        address=application_data.address,
        requested_amount=application_data.requested_amount,
        loan_purpose=application_data.loan_purpose,
        alternative_data=application_data.alternative_data.dict(),
        status="pending"
    )
    
    # Loop invariant: application exists in database with valid ID
    assert application.id > 0
    
    # Step 2: Engineer features from application data
    features = prediction_service.engineer_features(application_data)
    
    # Loop invariant: features contain all required fields
    assert len(features.features) >= 10
    assert all(isinstance(v, (int, float)) for v in features.features.values())
    
    # Step 3: Predict credit score using ML model
    score_result = prediction_service.predict_credit_score(features)
    
    # Loop invariant: score is within valid range
    assert 300 <= score_result.credit_score <= 850
    assert 0 <= score_result.default_probability <= 1
    
    # Step 4: Store credit score in database
    credit_score = db.create_credit_score(
        application_id=application.id,
        credit_score=score_result.credit_score,
        default_probability=score_result.default_probability,
        risk_category=score_result.risk_category,
        shap_explanations=[exp.dict() for exp in score_result.shap_explanations],
        model_version=score_result.model_version
    )
    
    # Step 5: Update application status based on score
    if score_result.credit_score >= 700:
        application.status = "approved"
    elif score_result.credit_score >= 600:
        application.status = "under_review"
    else:
        application.status = "rejected"
    
    db.update_application(application)
    
    # Postconditions
    assert application.status in ["approved", "under_review", "rejected"]
    assert credit_score.application_id == application.id
    
    return CreditApplicationResponse(
        application_id=application.id,
        user_id=application.user_id,
        applicant_type=application.applicant_type,
        status=application.status,
        requested_amount=application.requested_amount,
        credit_score=score_result.credit_score,
        risk_category=score_result.risk_category,
        created_at=application.created_at,
        updated_at=application.updated_at
    )
```

**Preconditions:**
- application_data is validated and non-null
- user_id corresponds to authenticated user
- Age is at least 18
- Requested amount is positive
- Database connection is active

**Postconditions:**
- Application record created in database
- Credit score computed and stored
- Application status updated based on score
- SHAP explanations generated
- Response contains all required fields

**Loop Invariants:**
- Application ID remains valid throughout process
- Feature vector maintains required dimensionality
- Credit score stays within 300-850 range
- Database consistency maintained at each step


### Feature Engineering Algorithm

```python
def engineer_features(application_data: CreditApplicationCreate) -> FeatureVector:
    """
    Extract and engineer features from raw application data.
    Handles missing values and creates derived features.
    
    INPUT: application_data (raw application form data)
    OUTPUT: FeatureVector with engineered features
    """
    # Preconditions
    assert application_data is not None
    assert application_data.alternative_data is not None
    
    features = {}
    alt_data = application_data.alternative_data
    
    # Step 1: Extract basic demographic features
    features['age'] = application_data.age
    features['requested_amount'] = application_data.requested_amount
    features['age_squared'] = application_data.age ** 2
    features['log_requested_amount'] = np.log1p(application_data.requested_amount)
    
    # Step 2: Extract alternative data features with missing value handling
    features['monthly_income'] = alt_data.monthly_income if alt_data.monthly_income else 0.0
    features['has_income_data'] = 1 if alt_data.monthly_income else 0
    
    # Step 3: Applicant-type specific features
    if application_data.applicant_type == "unbanked":
        features['remittance_frequency'] = alt_data.remittance_frequency or 0
        features['community_score'] = alt_data.community_verification_score or 0.0
        features['microfinance_count'] = alt_data.microfinance_repayment_count or 0
        features['has_community_verification'] = 1 if alt_data.community_verification_score else 0
        
        # Derived features for unbanked
        features['remittance_reliability'] = min(features['remittance_frequency'] / 12.0, 1.0)
        features['community_trust_score'] = features['community_score'] / 10.0
        
    elif application_data.applicant_type == "underbanked":
        features['gig_rating'] = alt_data.gig_platform_rating or 0.0
        features['upi_frequency'] = alt_data.upi_transaction_frequency or 0
        features['savings_balance'] = alt_data.savings_account_balance or 0.0
        features['has_gig_data'] = 1 if alt_data.gig_platform_rating else 0
        
        # Derived features for underbanked
        features['gig_reliability'] = features['gig_rating'] / 5.0
        features['digital_activity'] = min(features['upi_frequency'] / 30.0, 1.0)
        features['savings_ratio'] = features['savings_balance'] / max(features['requested_amount'], 1.0)
    
    # Step 4: Create interaction features
    if features['monthly_income'] > 0:
        features['debt_to_income_ratio'] = features['requested_amount'] / (features['monthly_income'] * 12)
    else:
        features['debt_to_income_ratio'] = 0.0
    
    # Step 5: Normalize and clip features
    for key in features:
        if isinstance(features[key], float):
            features[key] = np.clip(features[key], -10.0, 10.0)
    
    feature_names = sorted(features.keys())
    
    # Postconditions
    assert len(features) >= 10
    assert all(isinstance(v, (int, float)) for v in features.values())
    assert not any(np.isnan(v) for v in features.values())
    assert not any(np.isinf(v) for v in features.values())
    
    return FeatureVector(features=features, feature_names=feature_names)
```

**Preconditions:**
- application_data is validated and non-null
- alternative_data field is present
- Applicant type is either "unbanked" or "underbanked"

**Postconditions:**
- Feature vector contains at least 10 features
- All feature values are numeric (int or float)
- No NaN or infinite values in features
- Features are normalized and clipped to valid ranges
- Feature names are sorted for consistency

**Loop Invariants:**
- All processed features remain numeric
- Missing values are properly imputed with 0 or default
- Feature dictionary maintains consistency throughout processing


### Credit Score Prediction Algorithm

```python
def predict_credit_score(features: FeatureVector) -> CreditScoreResult:
    """
    Predict credit score using pre-trained XGBoost model and generate SHAP explanations.
    
    INPUT: features (engineered feature vector)
    OUTPUT: CreditScoreResult with score, probability, risk category, and explanations
    """
    # Preconditions
    assert features is not None
    assert len(features.features) >= 10
    assert model is not None
    assert shap_explainer is not None
    
    # Step 1: Prepare feature array in correct order
    feature_array = np.array([features.features[name] for name in features.feature_names])
    feature_array = feature_array.reshape(1, -1)
    
    # Loop invariant: feature array has correct shape
    assert feature_array.shape[0] == 1
    assert feature_array.shape[1] == len(features.feature_names)
    
    # Step 2: Predict default probability using XGBoost
    default_probability = model.predict_proba(feature_array)[0, 1]
    
    # Loop invariant: probability is valid
    assert 0 <= default_probability <= 1
    
    # Step 3: Convert probability to credit score (300-850 scale)
    # Lower default probability = higher credit score
    # Using inverse logistic transformation
    credit_score = 300 + (850 - 300) * (1 - default_probability)
    credit_score = np.clip(credit_score, 300, 850)
    
    # Loop invariant: credit score is within valid range
    assert 300 <= credit_score <= 850
    
    # Step 4: Determine risk category
    if credit_score >= 700:
        risk_category = "low"
    elif credit_score >= 600:
        risk_category = "medium"
    else:
        risk_category = "high"
    
    # Step 5: Generate SHAP explanations
    shap_values = shap_explainer.shap_values(feature_array)
    
    # Get top 10 most impactful features
    feature_importance = []
    for i, feature_name in enumerate(features.feature_names):
        shap_value = shap_values[0][i]
        feature_value = features.features[feature_name]
        impact = "positive" if shap_value > 0 else "negative"
        
        feature_importance.append(
            SHAPExplanation(
                feature_name=feature_name,
                feature_value=feature_value,
                shap_value=float(shap_value),
                impact=impact
            )
        )
    
    # Sort by absolute SHAP value and take top 10
    feature_importance.sort(key=lambda x: abs(x.shap_value), reverse=True)
    top_explanations = feature_importance[:10]
    
    # Postconditions
    assert 300 <= credit_score <= 850
    assert 0 <= default_probability <= 1
    assert risk_category in ["low", "medium", "high"]
    assert len(top_explanations) <= 10
    
    return CreditScoreResult(
        credit_score=float(credit_score),
        default_probability=float(default_probability),
        risk_category=risk_category,
        shap_explanations=top_explanations,
        model_version="xgboost_v1.0"
    )
```

**Preconditions:**
- features is non-null with at least 10 features
- ML model is loaded and ready
- SHAP explainer is initialized
- All feature values are numeric and valid

**Postconditions:**
- Credit score is between 300 and 850
- Default probability is between 0 and 1
- Risk category is one of: "low", "medium", "high"
- SHAP explanations contain top 10 most impactful features
- All numeric values are finite (no NaN or infinity)

**Loop Invariants:**
- Feature array maintains correct dimensionality
- Probability remains in [0, 1] range
- Credit score stays within [300, 850] range
- SHAP values are computed for all features


### User Authentication Algorithm

```python
def authenticate_user(credentials: UserLogin) -> TokenResponse:
    """
    Authenticate user with email/password and generate JWT token.
    
    INPUT: credentials (email and password)
    OUTPUT: TokenResponse with JWT token and user info
    """
    # Preconditions
    assert credentials is not None
    assert credentials.email is not None
    assert credentials.password is not None
    assert len(credentials.password) >= 8
    
    # Step 1: Query user from database by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Step 2: Verify user exists
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Loop invariant: user exists in database
    assert user.id > 0
    assert user.hashed_password is not None
    
    # Step 3: Verify password hash
    password_valid = bcrypt.checkpw(
        credentials.password.encode('utf-8'),
        user.hashed_password.encode('utf-8')
    )
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Step 4: Generate JWT token
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    access_token = jwt.encode(
        token_payload,
        SECRET_KEY,
        algorithm="HS256"
    )
    
    # Postconditions
    assert access_token is not None
    assert len(access_token) > 0
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role
    )
```

**Preconditions:**
- credentials contain valid email and password
- Password is at least 8 characters
- Database connection is active
- SECRET_KEY is configured

**Postconditions:**
- JWT token is generated and valid
- Token contains user ID, email, and role
- Token expires in 24 hours
- User authentication is verified

**Loop Invariants:**
- User record remains consistent
- Password hash verification is secure
- Token payload contains required fields


## Key Functions with Formal Specifications

### Function 1: create_application()

```python
async def create_application(
    application_data: CreditApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CreditApplicationResponse:
    """Create new credit application and trigger scoring"""
    pass
```

**Preconditions:**
- current_user is authenticated (JWT token valid)
- application_data passes Pydantic validation
- application_data.age >= 18 and <= 100
- application_data.requested_amount > 0
- Database session is active
- At least 3 alternative data fields are provided

**Postconditions:**
- Application record created in database with unique ID
- Credit score computed and stored
- Application status set based on score (approved/under_review/rejected)
- Returns CreditApplicationResponse with all fields populated
- Database transaction committed successfully
- No side effects on input data

**Loop Invariants:** N/A (no loops in main function body)

### Function 2: predict_credit_score()

```python
def predict_credit_score(features: FeatureVector) -> CreditScoreResult:
    """Predict credit score and generate SHAP explanations"""
    pass
```

**Preconditions:**
- features is non-null FeatureVector
- features.features contains at least 10 numeric values
- All feature values are finite (no NaN or infinity)
- ML model is loaded in memory
- SHAP explainer is initialized

**Postconditions:**
- Returns CreditScoreResult with valid credit_score (300-850)
- default_probability is between 0 and 1
- risk_category is one of: "low", "medium", "high"
- shap_explanations contains top 10 features by absolute impact
- model_version is set to current version string
- No mutations to input features

**Loop Invariants:**
- For SHAP computation loop: All processed features have valid SHAP values
- Feature importance list maintains sorted order by absolute SHAP value

### Function 3: engineer_features()

```python
def engineer_features(application_data: CreditApplicationCreate) -> FeatureVector:
    """Extract and engineer features from application data"""
    pass
```

**Preconditions:**
- application_data is validated CreditApplicationCreate instance
- alternative_data field is present (not None)
- applicant_type is either "unbanked" or "underbanked"

**Postconditions:**
- Returns FeatureVector with at least 10 features
- All feature values are numeric (int or float)
- No NaN or infinite values in feature dictionary
- Features are normalized and clipped to [-10, 10] range
- feature_names list is sorted alphabetically
- Missing values are imputed with appropriate defaults (0 or 0.0)

**Loop Invariants:**
- For feature processing loop: All processed features remain numeric
- Feature dictionary maintains key-value consistency


### Function 4: authenticate_user()

```python
def authenticate_user(credentials: UserLogin, db: Session) -> TokenResponse:
    """Authenticate user and generate JWT token"""
    pass
```

**Preconditions:**
- credentials contains valid email format
- credentials.password is at least 8 characters
- Database session is active
- SECRET_KEY environment variable is set

**Postconditions:**
- Returns TokenResponse with valid JWT token if authentication succeeds
- Raises HTTPException(401) if email not found or password invalid
- Token contains user_id, email, and role in payload
- Token expires in 24 hours from generation
- No password is stored or logged in plain text

**Loop Invariants:** N/A (no loops in function)

### Function 5: generate_shap_explanation()

```python
def generate_shap_explanation(
    features: FeatureVector, 
    prediction: float
) -> List[SHAPExplanation]:
    """Generate SHAP values for model transparency"""
    pass
```

**Preconditions:**
- features is valid FeatureVector with numeric values
- prediction is the model's output for these features
- SHAP explainer is initialized with model
- Feature names match model's expected features

**Postconditions:**
- Returns list of SHAPExplanation objects
- List contains top 10 features by absolute SHAP value
- Each explanation has feature_name, feature_value, shap_value, and impact
- impact is "positive" if shap_value > 0, else "negative"
- List is sorted by absolute SHAP value (descending)
- Sum of SHAP values approximates (prediction - base_value)

**Loop Invariants:**
- For SHAP computation: All features maintain their original values
- For sorting loop: Previously sorted elements remain in order

## Example Usage

### Example 1: Complete Credit Application Flow

```python
# Frontend: User submits credit application
import axios from 'axios';

const applicationData = {
  applicant_type: "underbanked",
  full_name: "Priya Sharma",
  age: 28,
  phone_number: "+91-9876543210",
  address: "123 MG Road, Bangalore, Karnataka",
  requested_amount: 50000,
  loan_purpose: "Small business expansion",
  alternative_data: {
    monthly_income: 25000,
    employment_type: "gig_worker",
    gig_platform_rating: 4.7,
    upi_transaction_frequency: 45,
    savings_account_balance: 15000
  }
};

const response = await axios.post(
  'http://localhost:8000/api/v1/applications',
  applicationData,
  {
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    }
  }
);

console.log('Credit Score:', response.data.credit_score);
console.log('Risk Category:', response.data.risk_category);
console.log('Status:', response.data.status);
```

### Example 2: Backend API Endpoint Implementation

```python
# Backend: FastAPI endpoint for creating application
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/applications", response_model=CreditApplicationResponse)
async def create_application(
    application_data: CreditApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new credit application and generate score"""
    
    # Validate user has not exceeded application limit
    recent_apps = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    if recent_apps >= 3:
        raise HTTPException(
            status_code=429,
            detail="Maximum 3 applications per month allowed"
        )
    
    # Create application
    application = Application(
        user_id=current_user.id,
        applicant_type=application_data.applicant_type,
        full_name=application_data.full_name,
        age=application_data.age,
        phone_number=application_data.phone_number,
        address=application_data.address,
        requested_amount=application_data.requested_amount,
        loan_purpose=application_data.loan_purpose,
        alternative_data=application_data.alternative_data.dict(),
        status="pending"
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    # Generate credit score
    prediction_service = PredictionService(model_path="models/xgboost_model.pkl")
    features = prediction_service.engineer_features(application_data)
    score_result = prediction_service.predict_credit_score(features)
    
    # Store credit score
    credit_score = CreditScore(
        application_id=application.id,
        credit_score=score_result.credit_score,
        default_probability=score_result.default_probability,
        risk_category=score_result.risk_category,
        shap_explanations=[exp.dict() for exp in score_result.shap_explanations],
        model_version=score_result.model_version
    )
    
    db.add(credit_score)
    
    # Update application status
    if score_result.credit_score >= 700:
        application.status = "approved"
    elif score_result.credit_score >= 600:
        application.status = "under_review"
    else:
        application.status = "rejected"
    
    db.commit()
    
    return CreditApplicationResponse(
        application_id=application.id,
        user_id=application.user_id,
        applicant_type=application.applicant_type,
        status=application.status,
        requested_amount=application.requested_amount,
        credit_score=score_result.credit_score,
        risk_category=score_result.risk_category,
        created_at=application.created_at,
        updated_at=application.updated_at
    )
```


### Example 3: ML Model Training Script (Run Once)

```python
# scripts/train_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
import joblib
import shap

def train_credit_model():
    """Train XGBoost model on Give Me Some Credit dataset"""
    
    # Load dataset
    df = pd.read_csv('data/GiveMeSomeCredit.csv')
    
    # Feature engineering
    df['age_squared'] = df['age'] ** 2
    df['debt_ratio_log'] = np.log1p(df['DebtRatio'])
    df['monthly_income_log'] = np.log1p(df['MonthlyIncome'].fillna(0))
    
    # Handle missing values
    df = df.fillna(df.median())
    
    # Prepare features and target
    feature_cols = [
        'age', 'age_squared', 'DebtRatio', 'debt_ratio_log',
        'MonthlyIncome', 'monthly_income_log', 
        'NumberOfOpenCreditLinesAndLoans',
        'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines',
        'NumberOfTime60-89DaysPastDueNotWorse',
        'NumberOfDependents'
    ]
    
    X = df[feature_cols]
    y = df['SeriousDlqin2yrs']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train XGBoost model
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1])
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    from sklearn.metrics import roc_auc_score, classification_report
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    print(f"Test AUC: {auc:.4f}")
    
    # Save model
    joblib.dump(model, 'models/xgboost_model.pkl')
    joblib.dump(feature_cols, 'models/feature_names.pkl')
    
    # Initialize SHAP explainer
    explainer = shap.TreeExplainer(model)
    joblib.dump(explainer, 'models/shap_explainer.pkl')
    
    print("Model training complete!")
    print(f"Model saved to: models/xgboost_model.pkl")
    print(f"Expected AUC: {auc:.4f} (Target: 0.79+)")

if __name__ == "__main__":
    train_credit_model()
```

### Example 4: Frontend React Component

```typescript
// components/CreditApplicationForm.tsx
import React, { useState } from 'react';
import axios from 'axios';

interface AlternativeData {
  monthly_income?: number;
  employment_type?: string;
  gig_platform_rating?: number;
  upi_transaction_frequency?: number;
  savings_account_balance?: number;
}

interface ApplicationFormData {
  applicant_type: 'unbanked' | 'underbanked';
  full_name: string;
  age: number;
  phone_number: string;
  address: string;
  requested_amount: number;
  loan_purpose: string;
  alternative_data: AlternativeData;
}

export const CreditApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState<ApplicationFormData>({
    applicant_type: 'underbanked',
    full_name: '',
    age: 18,
    phone_number: '',
    address: '',
    requested_amount: 10000,
    loan_purpose: '',
    alternative_data: {}
  });
  
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const token = localStorage.getItem('jwt_token');
      const response = await axios.post(
        'http://localhost:8000/api/v1/applications',
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      setResult(response.data);
    } catch (error) {
      console.error('Application submission failed:', error);
      alert('Failed to submit application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="application-form">
      <h2>Credit Application</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Full Name"
          value={formData.full_name}
          onChange={(e) => setFormData({...formData, full_name: e.target.value})}
          required
        />
        
        <input
          type="number"
          placeholder="Age"
          value={formData.age}
          onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
          min={18}
          max={100}
          required
        />
        
        <input
          type="number"
          placeholder="Requested Amount"
          value={formData.requested_amount}
          onChange={(e) => setFormData({...formData, requested_amount: parseFloat(e.target.value)})}
          min={1000}
          required
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit Application'}
        </button>
      </form>
      
      {result && (
        <div className="result">
          <h3>Credit Score: {result.credit_score}</h3>
          <p>Risk Category: {result.risk_category}</p>
          <p>Status: {result.status}</p>
        </div>
      )}
    </div>
  );
};
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Credit Score Range Invariant

*For any* application and its associated credit score, the credit score value must be between 300 and 850 inclusive.

**Validates: Requirements 3.3**

### Property 2: Default Probability Validity

*For any* credit score prediction, the default probability must be between 0 and 1 inclusive.

**Validates: Requirements 3.4**

### Property 3: Risk Category Consistency

*For any* credit score, the risk category must be "low" when score ≥ 700, "medium" when 600 ≤ score < 700, and "high" when score < 600.

**Validates: Requirements 3.5, 3.6, 3.7, 3.8, 6.1, 6.2, 6.3**

### Property 4: Application Status Transitions

*For any* application with a credit score, the application status must be "approved" when score ≥ 700, "under_review" when 600 ≤ score < 700, and "rejected" when score < 600.

**Validates: Requirements 6.1, 6.2, 6.3**

### Property 5: Feature Engineering Completeness

*For any* credit application, feature engineering must produce at least 10 numeric features with no NaN or infinite values.

**Validates: Requirements 3.1, 3.2, 4.2**

### Property 6: Feature Value Clipping

*For any* engineered feature vector, all numeric feature values must be within the range [-10, 10].

**Validates: Requirements 4.6**

### Property 7: Password Hashing

*For any* user registration, the stored password must be a bcrypt hash, never plain text.

**Validates: Requirements 1.3, 14.1, 14.2**

### Property 8: JWT Token Structure

*For any* generated JWT token, it must contain user_id, email, and role in the payload, be signed with HS256, and expire in 24 hours.

**Validates: Requirements 1.5, 1.6, 9.1, 9.2, 9.3**

### Property 9: SHAP Explanation Completeness

*For any* credit score, SHAP explanations must contain at most 10 features, each with feature_name, feature_value, shap_value, and impact ("positive" or "negative").

**Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6**

### Property 10: One-to-One Application-Score Relationship

*For any* application, there must be at most one associated credit score record.

**Validates: Requirements 3.9, 10.3, 10.4**

### Property 11: Age Validation

*For any* credit application, the applicant age must be between 18 and 100 inclusive.

**Validates: Requirements 2.2, 9, 11.2**

### Property 12: Alternative Data Minimum Requirement

*For any* credit application, at least 3 alternative data fields must be non-null.

**Validates: Requirements 2.4**

### Property 13: Authorization Filtering

*For any* applicant user requesting their applications, the system must return only applications where user_id matches the authenticated user.

**Validates: Requirements 7.1, 7.2**

### Property 14: Phone Number Masking

*For any* application retrieved by a non-admin user, the phone number must be masked to show only the last 4 digits.

**Validates: Requirements 7.5, 14.4**

### Property 15: Admin Access to All Applications

*For any* admin user requesting applications, the system must return applications from all users without filtering by user_id.

**Validates: Requirements 8.1**

### Property 16: Database Unique Constraints

*For any* user, the email must be unique across all users. *For any* credit score, the application_id must be unique across all credit scores.

**Validates: Requirements 10.1, 10.3**

### Property 17: Input Validation Ranges

*For any* alternative data input, gig_platform_rating must be in [0, 5], community_verification_score must be in [0, 10], and all numeric fields must be non-negative where specified.

**Validates: Requirements 11.4, 11.5, 11.6**

### Property 18: Application Persistence

*For any* successfully created application, the system must commit the database transaction and return HTTP 201 with a valid application_id.

**Validates: Requirements 2.1, 2.8, 17.1**

### Property 19: Transaction Atomicity

*For any* credit score generation, the credit score and application status update must be stored in the same database transaction.

**Validates: Requirements 17.2**

### Property 20: Timestamp Management

*For any* application creation, created_at and updated_at timestamps must be set. *For any* application update, updated_at must be refreshed.

**Validates: Requirements 6.5, 17.4, 17.5**

### Property 21: Rate Limiting Per User

*For any* user, the system must reject application submissions when the user has 3 or more applications within the past 30 days.

**Validates: Requirements 2.7, 13.1, 13.5**

### Property 22: Feature Names Sorted

*For any* feature vector, the feature_names list must be sorted alphabetically.

**Validates: Requirements 4.7**

### Property 23: Derived Features Present

*For any* feature vector, it must include age_squared and log_requested_amount as derived features.

**Validates: Requirements 4.1, 4.5**

### Property 24: Type-Specific Features

*For any* unbanked application, features must include remittance_frequency, community_verification_score, and microfinance_repayment_count. *For any* underbanked application, features must include gig_platform_rating, upi_transaction_frequency, and savings_account_balance.

**Validates: Requirements 4.3, 4.4**

### Property 25: Debt-to-Income Calculation

*For any* application with monthly_income > 0, the feature vector must include debt_to_income_ratio calculated as requested_amount / (monthly_income × 12).

**Validates: Requirements 4.8**

### Property 26: SHAP Sorting

*For any* SHAP explanations list, the explanations must be sorted by absolute SHAP value in descending order.

**Validates: Requirements 5.6**

### Property 27: JSON Serialization

*For any* application, alternative_data must be stored as JSON in the database. *For any* credit score, SHAP explanations must be stored as JSON in the database.

**Validates: Requirements 10.7, 10.8, 5.8**

### Property 28: Pagination Defaults

*For any* application list request without skip parameter, skip defaults to 0. *For any* request without limit parameter, limit defaults to 100.

**Validates: Requirements 7.7, 7.8**

### Property 29: Status Validation

*For any* admin status update, the new status must be one of: "pending", "approved", "rejected", "under_review".

**Validates: Requirements 6.4**

### Property 30: Logging Completeness

*For any* authentication attempt, the system must log timestamp, email, and success/failure. *For any* credit score access, the system must log user_id, application_id, and timestamp. *For any* status change, the system must log admin_id and timestamp.

**Validates: Requirements 23.1, 23.2, 23.3**

### Property 31: No Sensitive Data in Logs

*For any* log entry, it must not contain passwords, JWT tokens, or other sensitive credentials.

**Validates: Requirements 14.3, 23.7**

### Property 32: Model Version Tracking

*For any* credit score, it must include the model_version field for traceability.

**Validates: Requirements 15.6**

### Property 33: Health Check Response Structure

*For any* health check request, the response must include status, version, database connection status, and model loading status.

**Validates: Requirements 19.2**


## Error Handling

### Error Scenario 1: Invalid Authentication

**Condition:** User provides incorrect email or password, or JWT token is expired/invalid.

**Response:** 
- Return HTTP 401 Unauthorized
- Error message: "Invalid email or password" or "Token expired"
- Do not reveal whether email exists (security)

**Recovery:**
- User must re-authenticate with valid credentials
- Frontend redirects to login page
- Clear invalid token from localStorage

### Error Scenario 2: Missing Required Fields

**Condition:** Credit application submitted with missing required fields or invalid data types.

**Response:**
- Return HTTP 422 Unprocessable Entity
- Pydantic validation errors with specific field names
- Example: "age: field required" or "requested_amount: ensure this value is greater than 0"

**Recovery:**
- Frontend displays validation errors next to form fields
- User corrects invalid fields and resubmits
- No database record created

### Error Scenario 3: Application Rate Limit Exceeded

**Condition:** User attempts to submit more than 3 applications within 30 days.

**Response:**
- Return HTTP 429 Too Many Requests
- Error message: "Maximum 3 applications per month allowed"
- Include retry-after header with reset time

**Recovery:**
- Frontend displays rate limit message with reset date
- User must wait until rate limit window resets
- Admin can manually override if needed

### Error Scenario 4: Model Prediction Failure

**Condition:** ML model fails to generate prediction due to corrupted model file, incompatible features, or runtime error.

**Response:**
- Log error with full stack trace
- Return HTTP 500 Internal Server Error
- Error message: "Credit scoring temporarily unavailable"
- Application status set to "under_review" instead of failing

**Recovery:**
- Application saved in database for manual review
- Admin notified via logging system
- Model health check endpoint alerts monitoring
- Fallback to manual underwriting process

### Error Scenario 5: Database Connection Failure

**Condition:** Database is unreachable or connection pool exhausted.

**Response:**
- Return HTTP 503 Service Unavailable
- Error message: "Service temporarily unavailable, please try again"
- Retry-After header set to 60 seconds

**Recovery:**
- FastAPI dependency injection handles connection retry
- SQLAlchemy connection pool auto-reconnects
- Frontend implements exponential backoff retry
- Health check endpoint reports database status

### Error Scenario 6: SHAP Explanation Generation Failure

**Condition:** SHAP explainer fails due to memory issues or incompatible feature dimensions.

**Response:**
- Log warning but do not fail entire request
- Return credit score without SHAP explanations
- shap_explanations field set to empty list
- Include warning flag in response

**Recovery:**
- Credit score still usable without explanations
- Admin reviews SHAP explainer configuration
- Fallback to feature importance from model
- User sees score but limited transparency

### Error Scenario 7: Unauthorized Access to Application

**Condition:** User attempts to access another user's application details.

**Response:**
- Return HTTP 403 Forbidden
- Error message: "You do not have permission to access this resource"
- Log security event for audit

**Recovery:**
- Frontend prevents navigation to unauthorized resources
- User can only view their own applications
- Admin role can view all applications

### Error Scenario 8: Invalid Feature Values

**Condition:** Feature engineering produces NaN, infinity, or out-of-range values.

**Response:**
- Clip values to valid ranges [-10, 10]
- Impute NaN with 0 or median
- Log warning about data quality
- Continue with corrected features

**Recovery:**
- Prediction proceeds with sanitized features
- Data quality metrics tracked for monitoring
- Admin reviews applications with data quality issues
- Consider requesting additional information from user


## Testing Strategy

### Unit Testing Approach

**Objective:** Test individual components in isolation with mocked dependencies.

**Key Test Cases:**

1. **Authentication Service Tests**
   - Test password hashing with bcrypt
   - Test JWT token generation with correct payload
   - Test token verification with valid/expired tokens
   - Test user registration with duplicate email (should fail)
   - Test login with invalid credentials (should fail)

2. **Feature Engineering Tests**
   - Test feature extraction for unbanked applicants
   - Test feature extraction for underbanked applicants
   - Test missing value imputation (NaN → 0)
   - Test feature clipping to [-10, 10] range
   - Test derived feature calculations (debt-to-income ratio)
   - Test that output has no NaN or infinite values

3. **Prediction Service Tests**
   - Test credit score calculation from probability
   - Test risk category assignment at boundaries (599, 600, 699, 700)
   - Test SHAP explanation generation (mock explainer)
   - Test model loading from file
   - Test prediction with edge case features (all zeros, all max values)

4. **Database Model Tests**
   - Test User model creation and validation
   - Test Application model with valid/invalid data
   - Test CreditScore one-to-one relationship with Application
   - Test cascade delete behavior
   - Test unique constraints (email, application_id)

**Coverage Goal:** 85%+ line coverage for all service modules

**Tools:** pytest, pytest-cov, pytest-mock

### Property-Based Testing Approach

**Objective:** Verify correctness properties hold for randomly generated inputs.

**Property Test Library:** Hypothesis (Python)

**Key Properties to Test:**

1. **Credit Score Range Property**
   ```python
   @given(features=st.dictionaries(
       keys=st.text(min_size=1),
       values=st.floats(min_value=-10, max_value=10, allow_nan=False)
   ))
   def test_credit_score_always_in_range(features):
       """Credit score must always be between 300 and 850"""
       if len(features) >= 10:
           feature_vector = FeatureVector(features=features, feature_names=sorted(features.keys()))
           result = prediction_service.predict_credit_score(feature_vector)
           assert 300 <= result.credit_score <= 850
   ```

2. **Feature Engineering No NaN Property**
   ```python
   @given(
       age=st.integers(min_value=18, max_value=100),
       requested_amount=st.floats(min_value=1000, max_value=1000000),
       monthly_income=st.one_of(st.none(), st.floats(min_value=0, max_value=1000000))
   )
   def test_feature_engineering_no_nan(age, requested_amount, monthly_income):
       """Feature engineering must never produce NaN values"""
       app_data = create_test_application(age, requested_amount, monthly_income)
       features = engineer_features(app_data)
       assert all(not np.isnan(v) for v in features.features.values())
       assert all(not np.isinf(v) for v in features.features.values())
   ```

3. **Risk Category Consistency Property**
   ```python
   @given(credit_score=st.floats(min_value=300, max_value=850))
   def test_risk_category_consistency(credit_score):
       """Risk category must match credit score thresholds"""
       risk = calculate_risk_category(credit_score)
       if credit_score >= 700:
           assert risk == "low"
       elif credit_score >= 600:
           assert risk == "medium"
       else:
           assert risk == "high"
   ```

4. **Application Status Transition Property**
   ```python
   @given(credit_score=st.floats(min_value=300, max_value=850))
   def test_status_matches_score(credit_score):
       """Application status must be consistent with credit score"""
       status = determine_status_from_score(credit_score)
       if credit_score >= 700:
           assert status == "approved"
       elif credit_score >= 600:
           assert status == "under_review"
       else:
           assert status == "rejected"
   ```

**Execution:** Run 100 random examples per property test

### Integration Testing Approach

**Objective:** Test complete workflows with real database and API endpoints.

**Key Integration Tests:**

1. **End-to-End Application Flow**
   - Register user → Login → Submit application → Verify score generated
   - Assert application record created in database
   - Assert credit score record created with valid values
   - Assert application status updated correctly

2. **Authentication Flow**
   - Register user with valid data
   - Login with correct credentials
   - Access protected endpoint with JWT token
   - Verify token expiration after 24 hours

3. **Admin Access Control**
   - Admin user can view all applications
   - Regular user can only view own applications
   - Unauthorized access returns 403

4. **Rate Limiting**
   - Submit 3 applications successfully
   - 4th application within 30 days returns 429
   - After 30 days, can submit again

5. **Database Relationships**
   - Create application with user_id
   - Verify foreign key constraint
   - Delete user and verify cascade behavior

**Test Database:** PostgreSQL test instance with Docker

**Tools:** pytest, pytest-asyncio, httpx (for API testing), testcontainers (for PostgreSQL)

**Setup/Teardown:** 
- Create fresh database schema before each test
- Rollback transactions after each test
- Use fixtures for test data


## Performance Considerations

### Response Time Requirements

**Target Latencies:**
- Credit application submission: < 2 seconds (p95)
- User authentication: < 500ms (p95)
- Application list retrieval: < 1 second (p95)
- Admin dashboard load: < 3 seconds (p95)

**Optimization Strategies:**

1. **Model Inference Optimization**
   - Load XGBoost model once at startup (singleton pattern)
   - Keep SHAP explainer in memory (avoid recomputation)
   - Use batch prediction if multiple applications queued
   - Consider model quantization for faster inference

2. **Database Query Optimization**
   - Index on user_id, email, created_at columns
   - Use database connection pooling (SQLAlchemy default: 5-20 connections)
   - Eager loading for relationships (avoid N+1 queries)
   - Pagination for list endpoints (default: 100 items per page)

3. **API Response Optimization**
   - Use Pydantic models for efficient serialization
   - Compress responses with gzip for large payloads
   - Return only necessary fields (exclude sensitive data)
   - Cache static content (frontend assets)

### Scalability Considerations

**Current MVP Limitations:**
- Single monolithic backend (no horizontal scaling)
- In-memory model loading (limited by RAM)
- Synchronous request processing

**Future Scaling Path (Post-MVP):**
- Separate prediction service as microservice
- Load balancer with multiple backend instances
- Redis cache for frequently accessed data
- Async task queue for non-blocking predictions
- Database read replicas for query scaling

### Resource Requirements

**Minimum Server Specifications:**
- CPU: 2 cores (for FastAPI + ML inference)
- RAM: 4GB (2GB for app, 1GB for model, 1GB for PostgreSQL)
- Storage: 10GB (database + model files + logs)
- Network: 100 Mbps

**Expected Throughput:**
- 10-20 concurrent users (semester project scale)
- 100-200 applications per day
- 1000-2000 API requests per day

### Model Performance Metrics

**Target ML Metrics:**
- AUC-ROC: ≥ 0.79 (industry standard for credit scoring)
- Precision at 80% recall: ≥ 0.60
- False positive rate: ≤ 20%
- Model inference time: < 100ms per prediction

**Monitoring:**
- Log prediction latency for each request
- Track model accuracy on labeled data (if available)
- Monitor feature distribution drift
- Alert if prediction latency exceeds 200ms


## Security Considerations

### Authentication & Authorization

**Security Measures:**

1. **Password Security**
   - Hash passwords with bcrypt (cost factor: 12)
   - Minimum password length: 8 characters
   - No password stored in plain text or logs
   - Password validation on registration

2. **JWT Token Security**
   - Sign tokens with HS256 algorithm
   - Store SECRET_KEY in environment variable (never in code)
   - Token expiration: 24 hours
   - Include user_id, email, role in payload
   - Validate token on every protected endpoint

3. **Role-Based Access Control (RBAC)**
   - Two roles: "applicant" and "admin"
   - Applicants can only view their own applications
   - Admins can view all applications and update statuses
   - Enforce authorization checks in API endpoints

### Data Protection

**Sensitive Data Handling:**

1. **Personal Identifiable Information (PII)**
   - Encrypt sensitive fields in database (future enhancement)
   - Do not log PII (names, phone numbers, addresses)
   - Mask phone numbers in API responses (show last 4 digits only)
   - GDPR compliance: right to deletion (implement user data export/delete)

2. **Financial Data**
   - Store requested amounts and income data securely
   - Do not expose credit scores to unauthorized users
   - Audit log for all credit score access
   - Comply with financial data regulations

3. **Database Security**
   - Use parameterized queries (SQLAlchemy ORM prevents SQL injection)
   - Restrict database user permissions (no DROP/ALTER in production)
   - Enable SSL/TLS for database connections
   - Regular database backups (daily)

### API Security

**Protection Mechanisms:**

1. **Input Validation**
   - Pydantic models validate all input data
   - Reject requests with invalid data types
   - Sanitize string inputs (prevent XSS)
   - Limit request payload size (max 1MB)

2. **Rate Limiting**
   - Application submission: 3 per user per 30 days
   - Login attempts: 5 per IP per 15 minutes (prevent brute force)
   - API requests: 100 per user per hour
   - Implement with middleware or Redis

3. **CORS Configuration**
   - Allow only frontend origin (http://localhost:3000 for dev)
   - Restrict allowed methods (GET, POST, PUT, DELETE)
   - Do not allow credentials from untrusted origins

4. **HTTPS Enforcement**
   - Use HTTPS in production (TLS 1.2+)
   - Redirect HTTP to HTTPS
   - Set Secure flag on cookies
   - HSTS header for browser security

### Model Security

**ML Model Protection:**

1. **Model Integrity**
   - Store model files with checksums (verify on load)
   - Version control for model files
   - Restrict file system access to model directory
   - Log model loading and version in use

2. **Adversarial Input Protection**
   - Clip feature values to valid ranges
   - Detect anomalous input patterns
   - Log suspicious applications for review
   - Rate limit predictions per user

3. **Model Explainability**
   - SHAP values provide transparency
   - Prevent model inversion attacks (do not expose raw model)
   - Limit SHAP explanation detail (top 10 features only)

### Compliance & Auditing

**Regulatory Compliance:**

1. **Fair Lending Practices**
   - Ensure model does not discriminate based on protected attributes
   - Document model training data and features used
   - Provide explanations for all credit decisions (SHAP)
   - Regular bias audits on model predictions

2. **Audit Logging**
   - Log all authentication attempts (success/failure)
   - Log all credit score access with user_id and timestamp
   - Log application status changes with admin_id
   - Retain logs for 90 days minimum

3. **Data Retention**
   - Store applications for 7 years (financial regulation)
   - Allow users to request data deletion (GDPR)
   - Anonymize data after retention period
   - Secure deletion of backups


## Dependencies

### Backend Dependencies (Python 3.10+)

**Core Framework:**
- `fastapi==0.104.1` - Modern web framework for building APIs
- `uvicorn[standard]==0.24.0` - ASGI server for FastAPI
- `pydantic==2.5.0` - Data validation using Python type hints

**Database:**
- `sqlalchemy==2.0.23` - SQL toolkit and ORM
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `alembic==1.12.1` - Database migration tool

**Authentication:**
- `python-jose[cryptography]==3.3.0` - JWT token handling
- `passlib[bcrypt]==1.7.4` - Password hashing with bcrypt
- `python-multipart==0.0.6` - Form data parsing

**Machine Learning:**
- `scikit-learn==1.3.2` - ML utilities and preprocessing
- `xgboost==2.0.2` - Gradient boosting model
- `shap==0.43.0` - Model explainability
- `numpy==1.26.2` - Numerical computing
- `pandas==2.1.3` - Data manipulation
- `joblib==1.3.2` - Model serialization

**Utilities:**
- `python-dotenv==1.0.0` - Environment variable management
- `pydantic-settings==2.1.0` - Settings management

**Development:**
- `pytest==7.4.3` - Testing framework
- `pytest-asyncio==0.21.1` - Async test support
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-mock==3.12.0` - Mocking utilities
- `hypothesis==6.92.1` - Property-based testing
- `httpx==0.25.2` - HTTP client for testing
- `black==23.11.0` - Code formatter
- `flake8==6.1.0` - Linting
- `mypy==1.7.1` - Type checking

### Frontend Dependencies (React + TypeScript)

**Core Framework:**
- `react==18.2.0` - UI library
- `react-dom==18.2.0` - React DOM rendering
- `typescript==5.3.2` - Type-safe JavaScript

**HTTP Client:**
- `axios==1.6.2` - Promise-based HTTP client

**Routing:**
- `react-router-dom==6.20.0` - Client-side routing

**UI Components:**
- `@mui/material==5.14.18` - Material-UI components (optional)
- `recharts==2.10.3` - Charts for SHAP visualization (optional)

**Development:**
- `vite==5.0.4` - Build tool and dev server
- `@vitejs/plugin-react==4.2.0` - React plugin for Vite
- `eslint==8.54.0` - Linting
- `prettier==3.1.0` - Code formatter

### Database

**PostgreSQL:**
- Version: 14+ (LTS version)
- Extensions: None required for MVP
- Connection pooling: SQLAlchemy default (5-20 connections)

### Infrastructure

**Containerization:**
- `Docker==24.0+` - Container runtime
- `Docker Compose==2.23+` - Multi-container orchestration

**Development Tools:**
- `Git==2.40+` - Version control
- `Make` - Build automation (optional)

### External Services (None for MVP)

**Note:** MVP does not require external services. All components run locally or in Docker containers.

**Future Considerations (Post-MVP):**
- AWS S3 or MinIO for model storage
- Redis for caching and rate limiting
- Sentry for error tracking
- Prometheus + Grafana for monitoring

### System Requirements

**Development Environment:**
- Operating System: Linux, macOS, or Windows with WSL2
- Python: 3.10 or higher
- Node.js: 18+ (for frontend)
- Docker: 24.0+ with Docker Compose
- RAM: 8GB minimum (16GB recommended)
- Storage: 20GB free space

**Production Environment (Minimal):**
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- Network: 100 Mbps
- OS: Ubuntu 22.04 LTS or similar


## Deployment Architecture

### Docker Compose Setup (MVP)

The MVP uses Docker Compose for simple local deployment and development.

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    container_name: credit-scoring-db
    environment:
      POSTGRES_USER: credituser
      POSTGRES_PASSWORD: creditpass
      POSTGRES_DB: credit_scoring
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U credituser"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: credit-scoring-api
    environment:
      DATABASE_URL: postgresql://credituser:creditpass@postgres:5432/credit_scoring
      SECRET_KEY: ${SECRET_KEY}
      MODEL_PATH: /app/models/xgboost_model.pkl
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./models:/app/models
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: credit-scoring-ui
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
    command: npm run dev -- --host

volumes:
  postgres_data:
```

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p /app/models

# Expose port
EXPOSE 8000

# Run database migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host"]
```

### Project Structure

```
ai-credit-scoring/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration settings
│   │   ├── database.py             # Database connection and session
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── application.py
│   │   │   └── credit_score.py
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── application.py
│   │   │   └── credit_score.py
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── credit_service.py
│   │   │   └── prediction_service.py
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── applications.py
│   │   │   └── admin.py
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       ├── security.py
│   │       └── dependencies.py
│   ├── tests/                      # Test files
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_credit_service.py
│   │   ├── test_prediction.py
│   │   └── test_integration.py
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── scripts/                    # Utility scripts
│   │   └── train_model.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── alembic.ini
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CreditApplicationForm.tsx
│   │   │   ├── ApplicationList.tsx
│   │   │   ├── CreditScoreDisplay.tsx
│   │   │   ├── Login.tsx
│   │   │   └── Register.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ApplicationPage.tsx
│   │   │   └── AdminPanel.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── models/                         # ML model files
│   ├── xgboost_model.pkl
│   ├── shap_explainer.pkl
│   └── feature_names.pkl
├── data/                           # Training data
│   └── GiveMeSomeCredit.csv
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── Makefile                        # Build automation
```

### Environment Variables

```bash
# .env.example
# Database
DATABASE_URL=postgresql://credituser:creditpass@localhost:5432/credit_scoring

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# Model
MODEL_PATH=models/xgboost_model.pkl
SHAP_EXPLAINER_PATH=models/shap_explainer.pkl

# API
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Application
PROJECT_NAME=AI Credit Scoring Platform
VERSION=1.0.0
DEBUG=True
```

### Deployment Commands

```bash
# Initial setup
make setup              # Create .env file and directories
make train-model        # Train ML model on dataset

# Development
make dev                # Start all services with Docker Compose
make backend-logs       # View backend logs
make frontend-logs      # View frontend logs
make db-migrate         # Run database migrations

# Testing
make test               # Run all tests
make test-unit          # Run unit tests only
make test-integration   # Run integration tests only
make coverage           # Generate coverage report

# Production
make build              # Build Docker images
make up                 # Start services in production mode
make down               # Stop all services
make clean              # Remove containers and volumes
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```


## API Specification

### REST API Endpoints

#### Authentication Endpoints

**POST /api/v1/auth/register**

Register new user account.

Request:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "role": "applicant"
}
```

Response (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com",
  "role": "applicant"
}
```

**POST /api/v1/auth/login**

Authenticate user and get JWT token.

Request:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com",
  "role": "applicant"
}
```

**GET /api/v1/auth/me**

Get current user information (requires authentication).

Headers:
```
Authorization: Bearer <jwt_token>
```

Response (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "applicant",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Application Endpoints

**POST /api/v1/applications**

Submit new credit application (requires authentication).

Headers:
```
Authorization: Bearer <jwt_token>
```

Request:
```json
{
  "applicant_type": "underbanked",
  "full_name": "Priya Sharma",
  "age": 28,
  "phone_number": "+91-9876543210",
  "address": "123 MG Road, Bangalore, Karnataka",
  "requested_amount": 50000,
  "loan_purpose": "Small business expansion",
  "alternative_data": {
    "monthly_income": 25000,
    "employment_type": "gig_worker",
    "gig_platform_rating": 4.7,
    "upi_transaction_frequency": 45,
    "savings_account_balance": 15000
  }
}
```

Response (201 Created):
```json
{
  "application_id": 42,
  "user_id": 1,
  "applicant_type": "underbanked",
  "status": "approved",
  "requested_amount": 50000,
  "credit_score": 725.5,
  "risk_category": "low",
  "created_at": "2024-01-15T10:35:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

**GET /api/v1/applications/{application_id}**

Get application details with credit score (requires authentication).

Headers:
```
Authorization: Bearer <jwt_token>
```

Response (200 OK):
```json
{
  "application_id": 42,
  "user_id": 1,
  "applicant_type": "underbanked",
  "full_name": "Priya Sharma",
  "age": 28,
  "phone_number": "+91-****3210",
  "address": "123 MG Road, Bangalore, Karnataka",
  "requested_amount": 50000,
  "loan_purpose": "Small business expansion",
  "status": "approved",
  "credit_score": 725.5,
  "default_probability": 0.15,
  "risk_category": "low",
  "shap_explanations": [
    {
      "feature_name": "gig_platform_rating",
      "feature_value": 4.7,
      "shap_value": 0.23,
      "impact": "positive"
    },
    {
      "feature_name": "monthly_income",
      "feature_value": 25000,
      "shap_value": 0.18,
      "impact": "positive"
    },
    {
      "feature_name": "age",
      "feature_value": 28,
      "shap_value": -0.05,
      "impact": "negative"
    }
  ],
  "created_at": "2024-01-15T10:35:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

**GET /api/v1/applications**

List user's applications (requires authentication).

Headers:
```
Authorization: Bearer <jwt_token>
```

Query Parameters:
- `skip` (optional, default: 0): Number of records to skip
- `limit` (optional, default: 100): Maximum records to return

Response (200 OK):
```json
{
  "total": 3,
  "applications": [
    {
      "application_id": 42,
      "applicant_type": "underbanked",
      "status": "approved",
      "requested_amount": 50000,
      "credit_score": 725.5,
      "risk_category": "low",
      "created_at": "2024-01-15T10:35:00Z"
    },
    {
      "application_id": 38,
      "applicant_type": "unbanked",
      "status": "under_review",
      "requested_amount": 30000,
      "credit_score": 650.0,
      "risk_category": "medium",
      "created_at": "2024-01-10T14:20:00Z"
    }
  ]
}
```

#### Admin Endpoints

**GET /api/v1/admin/applications**

List all applications (admin only).

Headers:
```
Authorization: Bearer <admin_jwt_token>
```

Query Parameters:
- `skip` (optional, default: 0)
- `limit` (optional, default: 100)
- `status` (optional): Filter by status

Response (200 OK):
```json
{
  "total": 150,
  "applications": [
    {
      "application_id": 42,
      "user_id": 1,
      "applicant_type": "underbanked",
      "full_name": "Priya Sharma",
      "status": "approved",
      "requested_amount": 50000,
      "credit_score": 725.5,
      "risk_category": "low",
      "created_at": "2024-01-15T10:35:00Z"
    }
  ]
}
```

**PUT /api/v1/admin/applications/{application_id}/status**

Update application status (admin only).

Headers:
```
Authorization: Bearer <admin_jwt_token>
```

Request:
```json
{
  "status": "approved"
}
```

Response (200 OK):
```json
{
  "application_id": 42,
  "status": "approved",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**GET /api/v1/admin/statistics**

Get platform statistics (admin only).

Headers:
```
Authorization: Bearer <admin_jwt_token>
```

Response (200 OK):
```json
{
  "total_applications": 150,
  "approved": 85,
  "rejected": 40,
  "under_review": 25,
  "average_credit_score": 680.5,
  "total_users": 120,
  "applications_today": 12
}
```

#### Health Check Endpoint

**GET /health**

Check API health status (no authentication required).

Response (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "model": "loaded"
}
```

### Error Responses

**400 Bad Request**
```json
{
  "detail": "Invalid request data"
}
```

**401 Unauthorized**
```json
{
  "detail": "Invalid email or password"
}
```

**403 Forbidden**
```json
{
  "detail": "You do not have permission to access this resource"
}
```

**404 Not Found**
```json
{
  "detail": "Application not found"
}
```

**422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "ensure this value is greater than or equal to 18",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**429 Too Many Requests**
```json
{
  "detail": "Maximum 3 applications per month allowed",
  "retry_after": 1209600
}
```

**500 Internal Server Error**
```json
{
  "detail": "Credit scoring temporarily unavailable"
}
```


## ML Model Training Pipeline

### Training Data Preparation

**Dataset:** Give Me Some Credit (Kaggle)
- Size: ~7 MB, 150,000 records
- Target: SeriousDlqin2yrs (binary: 0 = no default, 1 = default)
- Features: Age, DebtRatio, MonthlyIncome, NumberOfOpenCreditLinesAndLoans, etc.

**Data Preprocessing Steps:**

```python
def preprocess_training_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preprocess Give Me Some Credit dataset for model training.
    
    INPUT: df (raw dataset from CSV)
    OUTPUT: (X_processed, y) tuple with features and target
    """
    # Step 1: Handle missing values
    df['MonthlyIncome'] = df['MonthlyIncome'].fillna(df['MonthlyIncome'].median())
    df['NumberOfDependents'] = df['NumberOfDependents'].fillna(0)
    
    # Step 2: Remove outliers (DebtRatio > 10 is unrealistic)
    df = df[df['DebtRatio'] <= 10]
    
    # Step 3: Feature engineering
    df['age_squared'] = df['age'] ** 2
    df['debt_ratio_log'] = np.log1p(df['DebtRatio'])
    df['monthly_income_log'] = np.log1p(df['MonthlyIncome'])
    df['total_late_payments'] = (
        df['NumberOfTimes90DaysLate'] + 
        df['NumberOfTime60-89DaysPastDueNotWorse'] +
        df['NumberOfTime30-59DaysPastDueNotWorse']
    )
    df['has_real_estate'] = (df['NumberRealEstateLoansOrLines'] > 0).astype(int)
    
    # Step 4: Select features
    feature_cols = [
        'age', 'age_squared',
        'DebtRatio', 'debt_ratio_log',
        'MonthlyIncome', 'monthly_income_log',
        'NumberOfOpenCreditLinesAndLoans',
        'NumberOfTimes90DaysLate',
        'NumberRealEstateLoansOrLines',
        'NumberOfTime60-89DaysPastDueNotWorse',
        'NumberOfDependents',
        'total_late_payments',
        'has_real_estate'
    ]
    
    X = df[feature_cols]
    y = df['SeriousDlqin2yrs']
    
    return X, y
```

### Model Training Configuration

**XGBoost Hyperparameters:**

```python
model_config = {
    'n_estimators': 100,           # Number of boosting rounds
    'max_depth': 6,                # Maximum tree depth
    'learning_rate': 0.1,          # Step size shrinkage
    'subsample': 0.8,              # Row sampling ratio
    'colsample_bytree': 0.8,       # Column sampling ratio
    'min_child_weight': 1,         # Minimum sum of instance weight
    'gamma': 0,                    # Minimum loss reduction for split
    'reg_alpha': 0,                # L1 regularization
    'reg_lambda': 1,               # L2 regularization
    'scale_pos_weight': None,      # Computed from class imbalance
    'random_state': 42,
    'n_jobs': -1                   # Use all CPU cores
}
```

**Training Process:**

```python
def train_xgboost_model(X_train, y_train, X_val, y_val):
    """
    Train XGBoost classifier with early stopping.
    
    INPUT: Training and validation data
    OUTPUT: Trained XGBoost model
    """
    # Calculate class imbalance ratio
    scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
    
    # Initialize model
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        eval_metric='auc'
    )
    
    # Train with early stopping
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        early_stopping_rounds=10,
        verbose=True
    )
    
    return model
```

### Model Evaluation Metrics

**Primary Metric:** AUC-ROC (Area Under Receiver Operating Characteristic Curve)
- Target: ≥ 0.79
- Measures model's ability to distinguish between default and non-default

**Secondary Metrics:**
- Precision at 80% recall: Measures false positive rate at high recall
- F1-Score: Harmonic mean of precision and recall
- Confusion Matrix: True/false positives and negatives

**Evaluation Code:**

```python
def evaluate_model(model, X_test, y_test):
    """
    Evaluate model performance on test set.
    
    INPUT: Trained model and test data
    OUTPUT: Dictionary of evaluation metrics
    """
    from sklearn.metrics import (
        roc_auc_score, precision_recall_curve, 
        f1_score, confusion_matrix, classification_report
    )
    
    # Predict probabilities
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    auc = roc_auc_score(y_test, y_pred_proba)
    f1 = f1_score(y_test, y_pred)
    
    # Precision at 80% recall
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_pred_proba)
    idx = np.argmin(np.abs(recalls - 0.8))
    precision_at_80_recall = precisions[idx]
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    metrics = {
        'auc_roc': auc,
        'f1_score': f1,
        'precision_at_80_recall': precision_at_80_recall,
        'confusion_matrix': cm.tolist(),
        'classification_report': classification_report(y_test, y_pred)
    }
    
    print(f"AUC-ROC: {auc:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print(f"Precision at 80% Recall: {precision_at_80_recall:.4f}")
    print("\nConfusion Matrix:")
    print(cm)
    
    return metrics
```

### Model Persistence

**Saving Model Artifacts:**

```python
def save_model_artifacts(model, feature_names, output_dir='models'):
    """
    Save trained model, SHAP explainer, and metadata.
    
    INPUT: Trained model and feature names
    OUTPUT: Saved files in output_dir
    """
    import joblib
    import shap
    import json
    from datetime import datetime
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save XGBoost model
    model_path = os.path.join(output_dir, 'xgboost_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    
    # Save feature names
    features_path = os.path.join(output_dir, 'feature_names.pkl')
    joblib.dump(feature_names, features_path)
    print(f"Feature names saved to: {features_path}")
    
    # Initialize and save SHAP explainer
    explainer = shap.TreeExplainer(model)
    explainer_path = os.path.join(output_dir, 'shap_explainer.pkl')
    joblib.dump(explainer, explainer_path)
    print(f"SHAP explainer saved to: {explainer_path}")
    
    # Save metadata
    metadata = {
        'model_version': '1.0',
        'training_date': datetime.utcnow().isoformat(),
        'feature_count': len(feature_names),
        'model_type': 'XGBoost',
        'framework_version': xgboost.__version__
    }
    
    metadata_path = os.path.join(output_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {metadata_path}")
```

### Complete Training Script

**Location:** `backend/scripts/train_model.py`

**Usage:**
```bash
# Train model on Give Me Some Credit dataset
python backend/scripts/train_model.py --data data/GiveMeSomeCredit.csv --output models/

# Expected output:
# Training XGBoost model...
# [0]  validation_0-auc:0.85234
# [10] validation_0-auc:0.86123
# ...
# Test AUC: 0.8512
# Model saved to: models/xgboost_model.pkl
```

**Note:** This script should be run ONCE before deploying the MVP. The trained model is then loaded at application startup and used for all predictions.


## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Objectives:** Set up project structure, database, and basic authentication.

**Tasks:**
1. Initialize project repositories (backend, frontend)
2. Set up Docker Compose with PostgreSQL
3. Implement database models (User, Application, CreditScore)
4. Create Alembic migrations
5. Implement authentication service (JWT, bcrypt)
6. Create auth API endpoints (register, login, /me)
7. Write unit tests for authentication

**Deliverables:**
- Working authentication system
- Database schema created
- Docker environment running
- 80%+ test coverage for auth module

### Phase 2: ML Model Training (Week 2-3)

**Objectives:** Train and validate credit scoring model.

**Tasks:**
1. Download Give Me Some Credit dataset
2. Implement data preprocessing pipeline
3. Perform exploratory data analysis (EDA)
4. Engineer features from raw data
5. Train XGBoost model with cross-validation
6. Evaluate model (target AUC ≥ 0.79)
7. Initialize SHAP explainer
8. Save model artifacts (model, explainer, feature names)
9. Document model performance and limitations

**Deliverables:**
- Trained XGBoost model (AUC ≥ 0.79)
- SHAP explainer initialized
- Model artifacts saved in models/ directory
- Training documentation with metrics

### Phase 3: Prediction Service (Week 3-4)

**Objectives:** Implement ML inference and feature engineering.

**Tasks:**
1. Create PredictionService class
2. Implement feature engineering from application data
3. Implement credit score prediction
4. Implement SHAP explanation generation
5. Handle missing values and edge cases
6. Write unit tests for prediction service
7. Write property-based tests for feature engineering
8. Optimize model loading (singleton pattern)

**Deliverables:**
- Working prediction service
- Feature engineering pipeline
- SHAP explanations generated
- 85%+ test coverage for prediction module

### Phase 4: Credit Application API (Week 4-5)

**Objectives:** Build core credit application endpoints.

**Tasks:**
1. Create CreditService class
2. Implement POST /api/v1/applications endpoint
3. Implement GET /api/v1/applications/{id} endpoint
4. Implement GET /api/v1/applications (list) endpoint
5. Integrate prediction service with credit service
6. Implement rate limiting (3 applications per 30 days)
7. Add authorization checks (users can only view own applications)
8. Write integration tests for application flow
9. Test end-to-end: submit application → get score

**Deliverables:**
- Working application submission API
- Credit scoring integrated
- Rate limiting implemented
- End-to-end tests passing

### Phase 5: Frontend Development (Week 5-7)

**Objectives:** Build React frontend for user interaction.

**Tasks:**
1. Set up React + TypeScript + Vite project
2. Implement authentication pages (Login, Register)
3. Implement credit application form
4. Implement application list page
5. Implement credit score display with SHAP visualization
6. Add form validation and error handling
7. Implement JWT token management (localStorage)
8. Style UI with Material-UI or Tailwind CSS
9. Add loading states and error messages
10. Test frontend with backend API

**Deliverables:**
- Working React frontend
- All user flows implemented
- Responsive design
- Error handling and validation

### Phase 6: Admin Panel (Week 7-8)

**Objectives:** Build admin interface for application management.

**Tasks:**
1. Implement admin authentication check
2. Create GET /api/v1/admin/applications endpoint
3. Create PUT /api/v1/admin/applications/{id}/status endpoint
4. Create GET /api/v1/admin/statistics endpoint
5. Build admin dashboard UI
6. Implement application list with filters
7. Implement status update functionality
8. Add statistics visualization
9. Write tests for admin endpoints

**Deliverables:**
- Working admin panel
- Application management features
- Statistics dashboard
- Admin authorization enforced

### Phase 7: Testing & Documentation (Week 8-9)

**Objectives:** Comprehensive testing and documentation.

**Tasks:**
1. Write additional unit tests (target: 85% coverage)
2. Write property-based tests with Hypothesis
3. Write integration tests for all workflows
4. Perform manual testing of all features
5. Fix bugs and edge cases
6. Write API documentation (OpenAPI/Swagger)
7. Write deployment guide (README.md)
8. Write user guide with screenshots
9. Document known limitations and future work

**Deliverables:**
- 85%+ test coverage
- All tests passing
- Complete API documentation
- Deployment and user guides

### Phase 8: Deployment & Demo (Week 9-10)

**Objectives:** Deploy MVP and prepare demo presentation.

**Tasks:**
1. Test Docker Compose deployment
2. Create production environment variables
3. Set up database backups
4. Configure HTTPS (if deploying to cloud)
5. Perform security audit (basic)
6. Load test with sample data
7. Prepare demo presentation
8. Create demo video
9. Document lessons learned
10. Plan future enhancements

**Deliverables:**
- Deployed MVP (local or cloud)
- Demo presentation ready
- Project documentation complete
- Future roadmap defined

### Success Criteria

**Functional Requirements:**
- ✅ Users can register and login
- ✅ Users can submit credit applications
- ✅ System generates credit scores (300-850)
- ✅ System provides SHAP explanations
- ✅ Users can view their application history
- ✅ Admins can view all applications
- ✅ Admins can update application status

**Technical Requirements:**
- ✅ Model AUC ≥ 0.79
- ✅ API response time < 2 seconds (p95)
- ✅ Test coverage ≥ 85%
- ✅ All endpoints secured with JWT
- ✅ Docker Compose deployment works
- ✅ Database migrations automated

**Documentation Requirements:**
- ✅ API documentation (OpenAPI)
- ✅ Deployment guide
- ✅ User guide
- ✅ Model training documentation
- ✅ Architecture diagrams

### Future Enhancements (Post-MVP)

**Short-term (Next Semester):**
- Add email notifications for application status
- Implement password reset functionality
- Add more alternative data sources
- Improve SHAP visualization with charts
- Add application export (PDF/CSV)
- Implement audit logging

**Medium-term (6-12 months):**
- Separate prediction service as microservice
- Add Redis caching for performance
- Implement automated model retraining pipeline
- Add A/B testing for model versions
- Integrate with external data sources (APIs)
- Add mobile-responsive design improvements

**Long-term (1+ years):**
- Deploy to cloud (AWS/GCP/Azure)
- Implement Kubernetes orchestration
- Add real-time monitoring (Prometheus/Grafana)
- Implement feature store (Feast)
- Add model drift detection
- Integrate with payment gateways
- Build mobile app (React Native)
- Add multi-language support


## Summary

This design document describes a comprehensive MVP for an AI-powered credit scoring platform targeting unbanked and underbanked populations. The platform uses a simple 3-tier architecture with FastAPI backend, React/TypeScript frontend, and PostgreSQL database, deployable via Docker Compose for a semester EDI project.

**Key Design Decisions:**

1. **Monolithic Architecture:** Single backend service for rapid development, avoiding microservices complexity for MVP scope.

2. **Pre-trained Model:** Train XGBoost model once using Give Me Some Credit dataset, deploy as static artifact, avoiding automated retraining pipelines.

3. **SHAP Explainability:** Provide transparent credit decisions with top 10 feature explanations, addressing fairness and regulatory requirements.

4. **JWT Authentication:** Stateless authentication with role-based access control (applicant vs admin).

5. **PostgreSQL Database:** Reliable relational database with SQLAlchemy ORM for type-safe queries and Alembic migrations.

6. **Docker Compose Deployment:** Simple containerized deployment suitable for development and small-scale production.

**Technical Highlights:**

- Credit score range: 300-850 (FICO-compatible)
- Target model AUC: ≥ 0.79
- API response time: < 2 seconds (p95)
- Rate limiting: 3 applications per user per 30 days
- Test coverage: ≥ 85%
- Alternative data sources: 15+ fields for unbanked/underbanked populations

**Expected Impact:**

- Financial inclusion for 1.4B unbanked adults globally
- Improved risk assessment using alternative data
- Transparent credit decisions via SHAP explanations
- Cost-efficient alternative to manual underwriting
- Reduced predatory lending through accessible credit

This design balances technical rigor with practical constraints of a semester project, providing a solid foundation for future enhancements while delivering immediate value through a working MVP.
