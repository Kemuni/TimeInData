from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from APIParser import APIParser


class APIConnectionMiddleware(BaseMiddleware):
    """
    Outer middleware for creating httpx.AsyncClient and APIParser obj for our handlers and adding users info to database
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """ Create APIParser instance and pass it to the handler. Also update user info via API. """
        async with APIParser.create_client() as client:
            api = APIParser(client)
            await api.create_or_update_user(
                user_id=event.from_user.id,
                language=event.from_user.language_code,
                username=event.from_user.username,
            )

            data['api'] = api
            return await handler(event, data)
