from typing import Optional, List

from sqlalchemy import update, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database import func
from database.models import User


class BaseRepo:
    """ A class representing a base repository for handling database operations. """

    def __init__(self, session: AsyncSession):
        self.session = session


class UserRepo(BaseRepo):
    async def get_or_create(self, user_id: int, language: str, username: Optional[str] = None) -> None:
        """
        Creates or updates a new user in the database.
        :param user_id: The user's telegram ID.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        """
        insert_stmt = (
            insert(User)
            .values(
                user_id=user_id,
                username=username,
                language=language,
            )
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_=dict(
                    username=username,
                    language=language,
                    last_activity=func.utcnow(),
                ),
            )
        )

        await self.session.execute(insert_stmt)
        await self.session.commit()

    async def update_notify_hours(self, user_id: int, new_hours: List[int]) -> None:
        """
        Updated user notify hours in the database.
        :param user_id: The user's telegram ID.
        :param new_hours: The new user's hours to notify.
        """
        update_stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(notify_hours=new_hours)
        )

        await self.session.execute(update_stmt)
        await self.session.commit()

    async def get_notify_hours(self, user_id: int) -> List[int]:
        """
        Get user notify hours from the database.
        :param user_id: The user's telegram ID.
        :return: List with user notify hours.
        """
        select_stmt = (
            select(User.notify_hours)
            .where(User.user_id == user_id)
        )

        result = await self.session.execute(select_stmt)
        return result.scalar_one()


class DatabaseRepo(BaseRepo):
    """
    Repository for handling database operations. This class holds all the repositories for the database models.
    """

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)
