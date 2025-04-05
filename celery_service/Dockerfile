FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

COPY ./celery_service/requirements.txt .
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

WORKDIR /app/
COPY ./celery_service /app/celery_service
COPY ./logger /app/logger
