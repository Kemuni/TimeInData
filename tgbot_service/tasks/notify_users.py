import asyncio

from aiogram import exceptions, Bot
from aiohttp import web
from loguru import logger

from tgbot_service.APIParser import APIParser
from tgbot_service.config import get_config

routes = web.RouteTableDef()

MAX_MSG_RETRIES: int = 5


async def send_message(bot: Bot, user_id: int, text: str, retry_counter: int = 0) -> bool:
    """
    Safely send message to the user.

    :param bot: Aiogram instance of the bot.
    :param user_id: The telegram ID of the recipient of the message.
    :param text: The text of message.
    :param retry_counter: Current number of attempts of message sending.
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
        if retry_counter >= MAX_MSG_RETRIES:
            return False
        return await send_message(bot, user_id, text, retry_counter=retry_counter + 1)
    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: Failed")
    else:
        logger.info(f"Target [ID:{user_id}]: Message has been sent.")
        return True
    return False


@routes.get("/tasks/tgbot/notify_users")
async def notify_users(request: web.Request) -> web.Response:
    """ Send message to all users who must be notified about setting activity """
    bot = Bot(token=get_config().tg_bot.token.get_secret_value(), parse_mode="HTML")
    async with APIParser.create_client() as client:
        user_ids = await APIParser(client).get_users_to_notify()

    message_counter = 0
    try:
        for user_id in user_ids:
            is_success = await send_message(
                bot, user_id, "It's time to set your activity! Type /set_activity command"
            )
            message_counter += 1 if is_success else 0
            await asyncio.sleep(0.05)
    finally:
        logger.info(f'{message_counter} from {len(user_ids)} notifications was successfully sent.')

    await bot.session.close()
    return web.Response(status=200, text="Notification successfully sent.")
