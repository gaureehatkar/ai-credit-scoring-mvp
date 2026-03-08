# Setup Instructions

## Step-by-Step Guide to Run the Platform

### 1. Download Dataset

**Option A: Using Kaggle CLI (Recommended)**

```bash
# Install Kaggle CLI
pip install kaggle

# Configure Kaggle credentials (get API token from kaggle.com/account)
# Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\Users\<username>\.kaggle\ (Windows)

# Create data directory
mkdir -p data

# Download dataset
kaggle competitions download -c GiveMeSomeCredit -p data/

# Unzip
cd data
unzip GiveMeSomeCredit.zip
cd ..
```

**Option B: Manual Download**

1. Go to Kaggle: https://www.kaggle.com/c/GiveMeSomeCredit/data
2. Download `cs-training.csv` (you'll need a Kaggle account)
3. Create a `data/` folder in the project root
4. Place `cs-training.csv` in the `data/` folder

### 2. Install Python Dependencies (for model training)

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Train the ML Model

```bash
python backend/scripts/train_model.py --data data/cs-training.csv --output models/
```

This will:
- Train an XGBoost model on the dataset
- Save the model to `models/xgboost_model.pkl`
- Save SHAP explainer to `models/shap_explainer.pkl`
- Target AUC: >= 0.79

Expected output:
```
Training XGBoost model...
Test AUC-ROC: 0.8512
✓ Model saved: models/xgboost_model.pkl
✓ SHAP explainer saved: models/shap_explainer.pkl
```

### 4. Configure Environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and change the SECRET_KEY to something secure.

### 5. Start Services with Docker Compose

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000
- React frontend on port 3000

### 6. Check Services are Running

```bash
# Check all services
docker-compose ps

# View backend logs
docker-compose logs -f backend

# Check health
curl http://localhost:8000/health
```

### 7. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 8. Create Admin User (Optional)

To create an admin user, register normally then update the database:

```bash
docker-compose exec postgres psql -U credituser -d credit_scoring

# In psql:
UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
\q
```

## Testing the Platform

### 1. Register a User
- Go to http://localhost:3000
- Click "Register"
- Fill in email, password, full name
- Click "Register"

### 2. Submit Credit Application
- Click "New Application"
- Fill in the form with sample data
- Submit
- You'll see your credit score immediately

### 3. View Applications
- Go to Dashboard
- See all your applications with scores

## Troubleshooting

### Model file not found
- Make sure you ran the training script
- Check that `models/xgboost_model.pkl` exists

### Database connection error
- Make sure Docker is running
- Check `docker-compose ps` shows postgres as healthy
- Wait 10-15 seconds for postgres to fully start

### Frontend can't connect to backend
- Check backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/.env`

### Port already in use
- Change ports in `docker-compose.yml`
- Or stop other services using those ports

## Stopping Services

```bash
docker-compose down
```

## Cleaning Up

```bash
# Remove containers and volumes
docker-compose down -v

# Remove models
rm -rf models/*.pkl
```
