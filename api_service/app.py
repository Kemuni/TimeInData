from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
        "__main__:app",
        host=get_config().api.host,
        port=get_config().api.port,
        log_config=LOGGING_CONFIG,
        reload=True,
    )


app = init_app()

if __name__ == '__main__':
    main()
