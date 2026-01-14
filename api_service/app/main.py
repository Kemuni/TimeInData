from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_config
from app.middlewares.network_auth import NetworkOrTMAAuthMiddleware
from app.utils.exception_handlers import pydantic_validation_exception_handler, general_exception_handler
from app.logger.log_conf import LOGGING_CONFIG
from app.msg_queue.message_publisher import message_publisher
from app.routers import routers_list
from loguru import logger


@asynccontextmanager
async def lifespan(_: FastAPI):
    await message_publisher.start()
    logger.info('Message publisher started!')
    yield
    await message_publisher.stop()
    logger.info('Message publisher stopped...')


def init_app() -> FastAPI:
    application = FastAPI(
        lifespan=lifespan,
        title="Time In Data API",
        description="API service for Time In Data project",
        version="1.0.0",
        docs_url='/docs' if get_config().debug else None,
        redoc_url='/redoc_url' if get_config().debug else None,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Middleware for checking if request is from trusted network or has valid TMA init data with fresh `auth_date`
    # Also set user id to request state
    application.add_middleware(
        NetworkOrTMAAuthMiddleware,
        allowed_networks=get_config().api.trusted_networks,
        tg_bot_token=get_config().api.tg_bot_token,
    )

    # Register exception handlers
    application.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)
    application.add_exception_handler(Exception, general_exception_handler)

    for router in routers_list:
        application.include_router(router)

    return application


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=get_config().api.host,
        port=get_config().api.port,
        log_config=LOGGING_CONFIG,
        workers=get_config().api.workers if not get_config().debug else None,
        reload=get_config().debug,
    )


app = init_app()

if __name__ == '__main__':
    main()
