from typing import AsyncGenerator

from fastapi import Depends, Request
from loguru import logger

from app.database.db import AsyncSessionLocal
from app.database.models import User
from app.database.repositories import DatabaseRepo


async def get_db() -> AsyncGenerator[DatabaseRepo, None]:
    """ Dependency for database session. Returns repository object. """
    async with AsyncSessionLocal() as session:
        try:
            yield DatabaseRepo(session=session)
        finally:
            await session.close()


async def get_user_from_state(request: Request, db: DatabaseRepo = Depends(get_db)) -> User:
    """ Dependency for getting user from request state. Creates user in the database if it doesn't exist. """
    db_user, is_created = await db.users.create_or_update(
        user_id=request.state.user_id,
        language=request.state.user_language,
        username=request.state.user_username,
    )

    if is_created:
        logger.info(f"New user {request.state.user_id} (@{request.state.user_username}) created in database.")

    return db_user
