from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import get_config
from logger.log_conf import LOGGING_CONFIG
from routers import routers_list


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database.session_manager import session_manager
    session_manager.init()
    yield
    await session_manager.close()


def init_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    for router in routers_list:
        app.include_router(router)

    return app


def main() -> None:
    uvicorn.run(init_app(), host=get_config().api.host, port=get_config().api.port, log_config=LOGGING_CONFIG)


if __name__ == '__main__':
    main()
