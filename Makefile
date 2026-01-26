.PHONY: setup test lint api dashboard compose-up compose-down download-data preprocess train train-all report e2e docker-backend docker-dashboard

PYTHON ?= python

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r backend/requirements.txt
	$(PYTHON) -m pip install -r ml/requirements.txt
	$(PYTHON) -m pip install -r dashboard/requirements.txt
	$(PYTHON) -m pip install ruff

test:
	pytest backend
	pytest ml -m "not tf_heavy"

lint:
	ruff check backend ml shared

api:
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down

docker-backend:
	docker build -t fraud-anomaly-backend -f backend/Dockerfile .

docker-dashboard:
	docker build -t fraud-anomaly-dashboard -f dashboard/Dockerfile .

download-data:
	./scripts/download_kaggle.sh

preprocess:
	$(PYTHON) -m ml.preprocess --raw data/raw/creditcard.csv --out data/processed

train-all:
	$(PYTHON) -m ml.train_all

# Backwards-compatible alias; prefer `make train-all`.
train: train-all
	@echo "Use 'make train-all' instead of 'make train'."

report:
	$(PYTHON) -m ml.evaluate --artifacts ml/artifacts --report reports/model_comparison.md

e2e: download-data preprocess train-all report