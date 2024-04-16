import asyncio
from datetime import datetime

from aiogram import exceptions, Bot
from loguru import logger

from database.repositories import UserRepo
from database.setup import create_engine, create_session_pool
from tgbot.config import get_config


async def send_message(bot: Bot, user_id: int, text: str) -> bool:
    """
    Safely send message to the user.

    :param bot: Aiogram instance of the bot.
    :param user_id: The telegram ID of the recipient of the message.
    :param text: The text of message.
    :return: True if message was successfully sent, False otherwise.
    """
    try:
        await bot.send_message(user_id, text)
    except exceptions.TelegramForbiddenError:
        logger.error(f"Target [ID:{user_id}]: Blocked by user")
    except exceptions.TelegramNotFound:
        logger.error(f"Target [ID:{user_id}]: Invalid user ID")
    except exceptions.TelegramRetryAfter as e:
        logger.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        return await send_message(bot, user_id, text)
    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: Failed")
    else:
        logger.info(f"Target [ID:{user_id}]: Message has been sent.")
        return True
    return False


async def get_user_ids_for_notification():
    """ Returns list of user ids that should be notified. """
    engine = create_engine(database_dsn=get_config().db.url)
    session_pool = create_session_pool(engine=engine)
    async with session_pool() as session:
        user_ids = await UserRepo(session).get_ids_to_notify(datetime.utcnow().hour)
    return user_ids


async def notify_users():
    """ Send message to all users who must be notified about setting activity """
    bot = Bot(token=get_config().tg_bot.token.get_secret_value(), parse_mode="HTML")
    user_ids = await get_user_ids_for_notification()

    try:
        for user_id in user_ids:
            await send_message(bot, user_id, "It's time to set your activity! Type /set_activity command")
            await asyncio.sleep(0.05)
    finally:
        logger.info('Messages successful sent.')

    await bot.session.close()
