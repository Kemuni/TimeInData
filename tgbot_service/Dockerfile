FROM python:3.10

ENV PYTHONUNBUFFERED=1

COPY ./tgbot_service/requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

ENV PYTHONPATH=/app

WORKDIR /app/
COPY ./tgbot_service /app/bot
COPY ./logger /app/logger

CMD ["python", "bot/main.py"]