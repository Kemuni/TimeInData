from typing import AsyncGenerator

from fastapi import Depends
from fastapi.exceptions import HTTPException
from loguru import logger
from starlette.status import HTTP_401_UNAUTHORIZED

from app.config import get_config
from app.database.db import AsyncSessionLocal
from app.database.models import User
from app.database.repositories import DatabaseRepo
from app.security.network_security import HTTPInternalNetworkUserAuth, HTTPInternalNetworkAuth
from app.security.schemas import HTTPUserCredentials, HTTPTMACredentials
from app.security.tma_init_data_security import HTTPTMAInitDataAuth


async def get_db() -> AsyncGenerator[DatabaseRepo, None]:
    """ Dependency for database session. Returns repository object. """
    async with AsyncSessionLocal() as session:
        try:
            yield DatabaseRepo(session=session)
        finally:
            await session.close()


tma_user_auth_schema = HTTPTMAInitDataAuth(
    tg_bot_token=get_config().api.tg_bot_token,
    auto_error=False
)
internal_network_user_auth_schema = HTTPInternalNetworkUserAuth(
    trusted_networks=get_config().api.trusted_networks,
    auto_error=False
)
only_internal_network_allowed = HTTPInternalNetworkAuth(
    trusted_networks=get_config().api.trusted_networks,
)


async def get_current_current_user(
    tma_user_credentials: HTTPTMACredentials = Depends(tma_user_auth_schema),
    internal_network_user_credentials: HTTPUserCredentials = Depends(internal_network_user_auth_schema),
    db: DatabaseRepo = Depends(get_db),
) -> User:
    """ Dependency for getting user from the database. Creates user in the database if it doesn't exist. """
    if internal_network_user_credentials:
        db_user, is_created = await db.users.create_or_update(
            user_id=internal_network_user_credentials.user_id,
            language=internal_network_user_credentials.language_code,
            username=internal_network_user_credentials.username,
        )
        user_from_service = "internal network"
    elif tma_user_credentials:
        db_user, is_created = await db.users.create_or_update(
            user_id=tma_user_credentials.user_id,
            language=tma_user_credentials.language_code,
            username=tma_user_credentials.username,
        )
        user_from_service = "TMA"
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if is_created:
        logger.info(f"New user {db_user.id} (@{db_user.username}) created in the database. User from {user_from_service}")

    return db_user
