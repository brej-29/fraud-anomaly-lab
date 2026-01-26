# Backend Dockerfile for FastAPI API (Hugging Face Spaces compatible)
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if needed, keep minimal)
RUN pip install --no-cache-dir --upgrade pip

COPY backend/requirements.txt /app/backend-requirements.txt
COPY ml/requirements.txt /app/ml-requirements.txt

RUN pip install --no-cache-dir -r /app/backend-requirements.txt \
    && pip install --no-cache-dir -r /app/ml-requirements.txt

COPY backend /app/backend
COPY ml /app/ml
COPY shared /app/shared

ENV PYTHONUNBUFFERED=1

# Use the PORT environment variable if provided (e.g., on Hugging Face Spaces).
CMD ["bash", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]