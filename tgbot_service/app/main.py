import asyncio
import logging
from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiohttp import web
from loguru import logger
from tenacity import RetryError

from app.config import get_config
from app.handlers import routers_list
from app.logger import configure_logger
from app.middlewares.api_connection_middleware import APIConnectionMiddleware
from app.pre_start_tasks import check_api_service_connection
from app.msg_queue.broker import rabbitmq_startup, rabbitmq_shutdown


async def pre_start_tasks() -> None:
    """ Complete all pre-start tasks for successfully starting our service """
    logger.info('Starting pre-start tasks...')
    startup_tasks = [
        check_api_service_connection(),
    ]
    for task in startup_tasks:
        try:
            await task
        except RetryError as e:
            logger.error(f"Caught error during pre task checking: {e}")
            raise e
    logger.info('Finish pre-start tasks!')

async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    logger.info('Bot startup event begin...')
    await pre_start_tasks()
    await bot.set_my_commands(
        commands=[
            BotCommand(command='start', description='Start menu'),
            BotCommand(command='settings', description='Open settings'),
            BotCommand(command='set_activity', description='Set activities'),
            BotCommand(command='summary', description='Get summary of your activities'),
        ]
    )

    if get_config().tg_bot.domain:
        await bot.set_webhook(f"{get_config().tg_bot.domain}{get_config().tg_bot.webhook_path}")
        logger.info('Webhook set successfully!')
    else:
        await bot.delete_webhook()
        logger.info('Webhook deleted successfully!')
    register_middlewares(dispatcher)
    dispatcher.include_routers(*routers_list)
    setup_dialogs(dispatcher)
    await rabbitmq_startup()
    logger.info('Bot startup event end!')


async def on_shutdown() -> None:
    logger.info('Bot shutdown event begin...')
    await rabbitmq_shutdown()
    logger.info('Bot shutdown event end!')

def register_middlewares(dp: Dispatcher) -> None:
    """ Register middlewares for messages and callback queries. """
    outer_middlewares = [
        APIConnectionMiddleware(),
    ]
    for middleware in outer_middlewares:
        logger.info(f'Registering middleware {middleware.__class__.__name__}...')
        dp.message.outer_middleware(middleware)
        dp.callback_query.outer_middleware(middleware)
        logger.info(f'Successfully registered middleware {middleware.__class__.__name__}!')


def get_storage() -> Union[RedisStorage, MemoryStorage]:
    """ Return storage based on the provided configuration. """
    if get_config().tg_bot.use_redis:
        logger.info('Using Redis storage')
        return RedisStorage.from_url(
            get_config().redis.url,
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        logger.info('Using Memory storage')
        return MemoryStorage()


def main() -> None:
    configure_logger(logging.INFO, supress_loggers=('httpx', 'httpcore'))

    # Creating main instances of aiogram for handling telegram user updates
    bot = Bot(
        token=get_config().tg_bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=get_storage(), events_isolation=SimpleEventIsolation(), skip_updates=True)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    if get_config().tg_bot.domain:
        # Create and setup AioHttp instances for aiogram updates to set up webhook
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_requests_handler.register(app, path=get_config().tg_bot.webhook_path)
        setup_application(app, dp, bot=bot)

        # Last step. Run application
        logger.info('Running webhook server...')
        web.run_app(app, host=get_config().tg_bot.host, port=get_config().tg_bot.port)
    else:
        logger.info('Starting polling...')
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
