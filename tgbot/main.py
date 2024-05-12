import asyncio
from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from loguru import logger

from logger.logger import LoggerCustomizer
from tgbot.config import get_config
from tgbot.handlers import routers_list
from tgbot.middlewares.api_connection_middleware import APIConnectionMiddleware


async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    logger.debug('Bot startup event begin.')
    register_middlewares(dispatcher)
    dispatcher.include_routers(*routers_list)
    setup_dialogs(dispatcher)
    logger.debug('Bot startup event end.')


def register_middlewares(dp: Dispatcher) -> None:
    """ Register middlewares for messages and callback queries. """
    outer_middlewares = [
        APIConnectionMiddleware(),
    ]
    for middleware in outer_middlewares:
        logger.debug(f'Registering middleware {middleware}.')
        dp.message.outer_middleware(middleware)
        dp.callback_query.outer_middleware(middleware)
        logger.debug(f'Successfully registered middleware {middleware}!')


def get_storage() -> Union[RedisStorage, MemoryStorage]:
    """ Return storage based on the provided configuration. """
    if get_config().tg_bot.use_redis:
        return RedisStorage.from_url(
            get_config().redis.url,
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main():
    LoggerCustomizer.init_loggers()

    bot = Bot(token=get_config().tg_bot.token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher(storage=get_storage(), events_isolation=SimpleEventIsolation())
    dp.startup.register(on_startup)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
