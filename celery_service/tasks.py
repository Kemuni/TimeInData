import asyncio

from celery_service.celery import app
from tgbot.tasks.notify_users import notify_users


@app.task
def send_hourly_tg_notification():
    """ Hourly notification in telegram to set their activities in bot """
    asyncio.run(notify_users())
