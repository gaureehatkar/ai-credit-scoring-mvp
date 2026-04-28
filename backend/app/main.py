from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import auth, applications, admin, admin_auth, admin_users, admin_applications, admin_analytics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(applications.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_users.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_applications.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_analytics.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    import os
    
    model_loaded = os.path.exists(settings.MODEL_PATH)
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "model_loaded": model_loaded
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Credit Scoring Platform API",
        "version": settings.VERSION,
        "docs": "/docs"
    }
