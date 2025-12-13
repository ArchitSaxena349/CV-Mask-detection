.PHONY: help install install-dev run test clean lint format

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt

run:  ## Run the development server
	python run.py

run-prod:  ## Run with production configuration
	FLASK_CONFIG=production python run.py

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=app --cov-report=html

lint:  ## Run linting
	flake8 app core
	isort --check-only app core

format:  ## Format code
	black app core
	isort app core

clean:  ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

setup:  ## Initial project setup
	python -m venv .venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source .venv/bin/activate  (Linux/Mac)"
	@echo "  .venv\\Scripts\\activate     (Windows)"

docker-build:  ## Build Docker image
	docker build -t mask-detector:latest .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 --name mask-detector mask-detector:latest

docker-compose-up:  ## Start with docker-compose
	docker-compose up -d

docker-compose-down:  ## Stop docker-compose
	docker-compose down

logs:  ## View application logs
	tail -f logs/mask_detector.log

security-scan:  ## Run security scan
	pip-audit

validate-config:  ## Validate configuration
	python -c "from core.validators import validate_config; from config import config; validate_config(config['development'])"