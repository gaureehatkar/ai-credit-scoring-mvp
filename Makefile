.PHONY: setup dev train-model test clean

setup:
	@echo "Setting up project..."
	@cp backend/.env.example backend/.env
	@mkdir -p data models
	@echo "✓ Setup complete. Edit backend/.env with your configuration."

train-model:
	@echo "Training ML model..."
	@cd backend && python scripts/train_model.py --data ../data/cs-training.csv --output ../models/

dev:
	@echo "Starting services..."
	@docker-compose up -d
	@echo "✓ Services started"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

logs:
	@docker-compose logs -f

backend-logs:
	@docker-compose logs -f backend

frontend-logs:
	@docker-compose logs -f frontend

test:
	@cd backend && pytest

coverage:
	@cd backend && pytest --cov=app tests/

down:
	@docker-compose down

clean:
	@docker-compose down -v
	@echo "✓ Cleaned up containers and volumes"

build:
	@docker-compose build
