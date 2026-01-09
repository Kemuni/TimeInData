from app.database.db import AsyncSessionLocal
from app.database.repositories import UserRepo
from app.msg_queue.message_publisher import message_publisher
from app.utils.utcnow import utcnow
from loguru import logger


async def remind_set_activities_job() -> None:
    """ Remind users to set activities via RabbitMQ """
    logger.info('Start "Set activities reminder" job')
    async with AsyncSessionLocal() as session:
        user_repo = UserRepo(session)
        notify_users_ids = await user_repo.get_ids_to_notify(utcnow().hour)
        if notify_users_ids:
            logger.info(f'Publish "Set activities reminder" for {len(notify_users_ids)} users')
            await message_publisher.publish_set_activities_reminder(notify_users_ids)
        else:
            logger.info('No users to publish with "Set activities reminder"')
    logger.info('End "Set activities reminder" job...')

