from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from pydantic import PostgresDsn

from database.repositories import DatabaseRepo
from database.setup import create_session_pool, create_engine


class DatabaseMiddleware(BaseMiddleware):
    """ Outer middleware for creating database session for our handlers and adding users info to database """

    def __init__(self, database_dsn: PostgresDsn, echo: bool = False):
        super().__init__()
        self.engine = create_engine(database_dsn=str(database_dsn), echo=echo)
        self.session_pool = create_session_pool(engine=self.engine)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """ Create database repository to work with database and pass it to the handler """
        async with self.session_pool() as session:
            db_repo = DatabaseRepo(session)
            await db_repo.users.get_or_create(
                user_id=event.from_user.id,
                language=event.from_user.language_code,
                username=event.from_user.username,
            )

            data['db'] = db_repo
            return await handler(event, data)
