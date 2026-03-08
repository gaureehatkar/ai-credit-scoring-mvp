# AI Credit Scoring MVP

An AI-powered credit scoring platform for unbanked and underbanked populations.

## Features
- 🤖 XGBoost ML model with 0.8394 AUC
- 🔍 SHAP explainability for transparency
- 👥 User authentication & role management
- 📊 Alternative data scoring (gig ratings, UPI transactions)
- 🎯 Automatic approval/rejection based on risk

## Quick Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-credit-scoring-mvp
cd ai-credit-scoring-mvp
```

### 2. Setup Database
```sql
CREATE DATABASE creditscoring;
CREATE USER credituser WITH PASSWORD 'creditpass123';
GRANT ALL PRIVILEGES ON DATABASE creditscoring TO credituser;
```

### 3. Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Demo Credentials
- Register any user to test
- Use sample data from the application form

## Tech Stack
- **Backend**: FastAPI, PostgreSQL, XGBoost, SHAP
- **Frontend**: React, TypeScript, Vite
- **ML**: scikit-learn, pandas, numpy
- **Auth**: JWT tokens, bcrypt

## Model Performance
- AUC-ROC: 0.8394 (exceeds 0.79 target)
- Dataset: Give Me Some Credit (Kaggle)
- Algorithm: XGBoost with class balancing