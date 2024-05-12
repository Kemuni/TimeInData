import httpx
from aiogram import Router, types, Bot
from aiogram.filters import ExceptionTypeFilter
from loguru import logger

from tgbot.config import get_config

router = Router()


@router.errors(ExceptionTypeFilter(httpx.ConnectError, httpx.HTTPStatusError))
async def handle_https_status_error(event: types.ErrorEvent, bot: Bot):
    exception = event.exception
    if isinstance(exception, httpx.ConnectError):
        logger.error(f"Connect Error. Unable to connect to server (URL: {exception.request.url}): {exception}")
    elif isinstance(exception, httpx.HTTPStatusError):
        logger.error(f"HTTP code error. Given {exception.response.status_code} (URL: {exception.request.url}): {exception}.")

    msg_text = get_config().msg_texts.error
    if event.update.message:
        await bot.send_message(event.update.message.chat.id, msg_text)
    else:
        await bot.answer_callback_query(event.update.callback_query.id, msg_text)
