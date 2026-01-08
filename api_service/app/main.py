from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_config
from app.logger.log_conf import LOGGING_CONFIG
from app.msg_queue.message_publisher import message_publisher
from app.routers import routers_list
from app.scheduler.scheduler import scheduler
from app.scheduler.jobs import remind_set_activities_job
from loguru import logger


@asynccontextmanager
async def lifespan(_: FastAPI):
    await message_publisher.start()
    logger.info('Message publisher started!')
    scheduler.start()
    logger.info('Scheduler started!')
    scheduler.add_job(
        remind_set_activities_job,
        'cron',
        hour='*',
        id='remind_set_activities_job',
        replace_existing=True,
    )
    logger.info('Hourly scheduler started!')
    yield
    scheduler.shutdown()
    logger.info('Scheduler stopped...')
    await message_publisher.stop()
    logger.info('Message publisher stopped...')


def init_app() -> FastAPI:
    application = FastAPI(lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in routers_list:
        application.include_router(router)

    return application


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=get_config().api.host,
        port=get_config().api.port,
        log_config=LOGGING_CONFIG,
        reload=True,
    )


app = init_app()

if __name__ == '__main__':
    main()
