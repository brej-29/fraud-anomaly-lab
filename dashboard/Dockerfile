# Dashboard Dockerfile for Streamlit app
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY dashboard/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY dashboard /app/dashboard
COPY shared /app/shared

ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]