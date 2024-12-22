import asyncio
from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiohttp import web
from loguru import logger
from tenacity import RetryError

from logger.logger import LoggerCustomizer
from tgbot_service.config import get_config
from tgbot_service.handlers import routers_list
from tgbot_service.middlewares.api_connection_middleware import APIConnectionMiddleware
from tgbot_service.pre_start_tasks import check_api_service_connection
from tgbot_service.tasks import task_routes_list


async def pre_start_tasks() -> None:
    """ Complete all pre start tasks for successfully starting our service """
    logger.info('Checking pre start tasks...')
    startup_tasks = [
        check_api_service_connection(),
    ]
    for task in startup_tasks:
        try:
            await task
        except RetryError as e:
            logger.error(f"Caught error during pre task checking: {e}")
            raise e
    logger.info('Finish pre start tasks!')

async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    logger.info('Bot startup event begin...')
    await pre_start_tasks()
    await bot.set_webhook(f"{get_config().tg_bot_domain}{get_config().tg_bot.webhook_path}")
    register_middlewares(dispatcher)
    dispatcher.include_routers(*routers_list)
    setup_dialogs(dispatcher)
    logger.info('Bot startup event end!')


def register_middlewares(dp: Dispatcher) -> None:
    """ Register middlewares for messages and callback queries. """
    outer_middlewares = [
        APIConnectionMiddleware(),
    ]
    for middleware in outer_middlewares:
        logger.info(f'Registering middleware {middleware}...')
        dp.message.outer_middleware(middleware)
        dp.callback_query.outer_middleware(middleware)
        logger.info(f'Successfully registered middleware {middleware}!')


def get_storage() -> Union[RedisStorage, MemoryStorage]:
    """ Return storage based on the provided configuration. """
    if get_config().tg_bot.use_redis:
        return RedisStorage.from_url(
            get_config().redis.url,
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


def main() -> None:
    LoggerCustomizer.init_loggers()

    # Creating main instances of aiogram for handling telegram user updates
    bot = Bot(token=get_config().tg_bot.token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher(storage=get_storage(), events_isolation=SimpleEventIsolation())
    dp.startup.register(on_startup)

    # Create and setup AioHttp instances for aiogram updates to set up webhook
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=get_config().tg_bot.webhook_path)
    setup_application(app, dp, bot=bot)
    app.router.add_routes(*task_routes_list)

    # Last step. Run application
    web.run_app(app, host=get_config().tg_bot.host, port=get_config().tg_bot.port)


if __name__ == "__main__":
    main()
