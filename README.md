# AI-Powered Credit Scoring Platform

An MVP platform for evaluating creditworthiness of unbanked and underbanked populations using machine learning and alternative data sources.

## Features

- User registration and JWT authentication
- Credit application submission with alternative data
- ML-based credit scoring (300-850 scale)
- SHAP explanations for transparency
- Admin panel for application management
- Docker Compose deployment

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, PostgreSQL, SQLAlchemy
- **ML**: XGBoost, scikit-learn, SHAP
- **Frontend**: React, TypeScript, Vite
- **Deployment**: Docker, Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.10+ (for model training)
- Node.js 18+ (for frontend development)

### Step 1: Download Dataset

```bash
# Install Kaggle CLI
pip install kaggle

# Download dataset (requires Kaggle API credentials)
mkdir -p data
kaggle competitions download -c GiveMeSomeCredit -p data/
cd data && unzip GiveMeSomeCredit.zip && cd ..
```

Or download manually from: https://www.kaggle.com/c/GiveMeSomeCredit/data

### Step 2: Train ML Model

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Train model
python scripts/train_model.py --data ../data/cs-training.csv --output ../models/

# Expected output: Test AUC >= 0.79
```

### Step 3: Start Services

```bash
# Copy environment file
cp backend/.env.example backend/.env

# Start all services with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### Step 4: Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
ai-credit-scoring/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── utils/            # Utilities
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── scripts/
│   │   └── train_model.py    # Model training script
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── Dockerfile
├── models/                    # ML model artifacts
├── data/                      # Training data
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Applications
- `POST /api/v1/applications` - Submit credit application
- `GET /api/v1/applications` - List user's applications
- `GET /api/v1/applications/{id}` - Get application details
- `GET /api/v1/applications/{id}/score` - Get credit score with SHAP explanations

### Admin
- `GET /api/v1/admin/applications` - List all applications
- `PUT /api/v1/admin/applications/{id}/status` - Update application status
- `GET /api/v1/admin/statistics` - Get platform statistics

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
cd backend
pytest
pytest --cov=app tests/
```

## Configuration

Edit `backend/.env` to configure:
- Database connection
- JWT secret key
- Model paths
- CORS origins

## License

MIT License - Educational Project
