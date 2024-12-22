import requests

from celery_service.celery import app
from celery_service.config import get_config


@app.task
def send_hourly_tg_notification() -> bool:
    """ Hourly notification in telegram to set their activities in bot """
    response = requests.get(f"{get_config().tg_bot_domain}{get_config().tg_bot.task_set_activity_notification_url}")
    response.raise_for_status()
    return response.status_code == 200
