from typing import AsyncGenerator

from database.db import AsyncSessionLocal
from database.repositories import DatabaseRepo


async def get_db() -> AsyncGenerator[DatabaseRepo, None]:
    """ Dependency for database session. Returns repository object. """
    async with AsyncSessionLocal() as session:
        try:
            yield DatabaseRepo(session=session)
        finally:
            await session.close()