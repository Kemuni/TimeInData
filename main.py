import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from loguru import logger

from logger.logger import LoggerCustomizer
from tgbot.config import get_config
from tgbot.handlers import routers_list


def get_storage() -> RedisStorage | MemoryStorage:
    """
    Return storage based on the provided configuration.
    """
    if get_config().tg_bot.use_redis:
        return RedisStorage.from_url(
            get_config().redis.dsn,
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main():
    LoggerCustomizer.init_loggers()

    bot = Bot(token=get_config().tg_bot.token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher(storage=get_storage())

    dp.include_routers(*routers_list)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот был выключен!")
