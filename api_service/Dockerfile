FROM python:3.10

ENV PYTHONUNBUFFERED=1

COPY ./api_service/requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

ENV PYTHONPATH=/app

WORKDIR /app/
COPY ./api_service /app/api
COPY ./logger /app/logger

# Создаем директорию для логов
RUN mkdir -p /logs && chmod 777 /logs

# Возвращаемся в /app и запускаем приложение
CMD ["python", "api/app.py"]
