from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging

from celery_service.config import get_config
from logger.logger import LoggerCustomizer

app = Celery('periodic_tasks', broker=get_config().celery_redis.url, include=['celery_service.tasks'])

app.conf.update(
    broker_connection_retry_on_startup=True,
    enable_utc=True,
)
app.conf.beat_schedule = {
    'hourly-tg-notification': {
        'task': 'celery_service.tasks.send_hourly_tg_notification',
        'schedule': crontab(minute='0'),
    }
}
app.conf.timezone = 'UTC'


@setup_logging.connect
def setup_logging(*args, **kwargs):
    LoggerCustomizer.customize_existing_loggers()
