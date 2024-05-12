from .database.session_manager import session_manager
from .database.repositories import DatabaseRepo


async def get_db():
    async with session_manager.create_session() as session:
        yield DatabaseRepo(session=session)
