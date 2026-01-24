# Backend Dockerfile for FastAPI API (Hugging Face Spaces compatible)
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if needed, keep minimal)
RUN pip install --no-cache-dir --upgrade pip

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY ml /app/ml
COPY shared /app/shared

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]