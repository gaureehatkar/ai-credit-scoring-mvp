from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://credituser:creditpass@localhost:5432/credit_scoring"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # Model paths
    MODEL_PATH: str = "models/xgboost_model.pkl"
    SHAP_EXPLAINER_PATH: str = "models/shap_explainer.pkl"
    FEATURE_NAMES_PATH: str = "models/feature_names.pkl"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Application
    PROJECT_NAME: str = "AI Credit Scoring Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
