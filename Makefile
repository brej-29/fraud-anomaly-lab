.PHONY: setup test api dashboard compose-up compose-down download-data preprocess train report e2e

PYTHON ?= python

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r backend/requirements.txt
	$(PYTHON) -m pip install -r ml/requirements.txt
	$(PYTHON) -m pip install -r dashboard/requirements.txt

test:
	pytest backend ml

api:
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down

download-data:
	./scripts/download_kaggle.sh

preprocess:
	$(PYTHON) -m ml.preprocess --raw data/raw/creditcard.csv --out data/processed

train:
	$(PYTHON) -m ml.train_all

report:
	$(PYTHON) -m ml.evaluate --artifacts ml/artifacts --report reports/model_comparison.md

e2e: download-data preprocess train report