from typing import AsyncGenerator

from app.database.db import AsyncSessionLocal
from app.database.repositories import DatabaseRepo


async def get_db() -> AsyncGenerator[DatabaseRepo, None]:
    """ Dependency for database session. Returns repository object. """
    async with AsyncSessionLocal() as session:
        try:
            yield DatabaseRepo(session=session)
        finally:
            await session.close()