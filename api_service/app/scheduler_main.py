""" Scheduler service runs in separate container """
import asyncio

from app.scheduler.scheduler import scheduler
from app.scheduler.jobs import remind_set_activities_job
from app.msg_queue.message_publisher import message_publisher
from loguru import logger


async def run_scheduler():
    await message_publisher.start()
    logger.info('Message publisher started!')

    scheduler.start()
    logger.info('Scheduler started!')

    # Run the job for reminding users to set their activities every hour at :00
    scheduler.add_job(
        remind_set_activities_job,
        'cron',
        hour='*', minute='0',
        id='remind_set_activities_job',
        replace_existing=True,
    )
    logger.info(f'Scheduler job added: {remind_set_activities_job.__name__} (runs every hour at :00)')

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info('Shutting down scheduler...')
        scheduler.shutdown()
        logger.info('Scheduler stopped!')
        await message_publisher.stop()
        logger.info('Message publisher stopped!')


if __name__ == '__main__':
    asyncio.run(run_scheduler())
