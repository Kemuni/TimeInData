from typing import Optional, List, Sequence

from sqlalchemy import update, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from .func import utcnow
from .models import User, Activity, Base


class BaseRepo:
    """ A class representing a base repository for handling database operations. """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_add(self, objs: List[Base]) -> None:
        """
        Add new objects from `objs` argument to the database.
        :param objs: A list of database model objects.
        """
        self.session.add_all(objs)
        await self.session.commit()


class UserRepo(BaseRepo):

    async def get_ids_to_notify(self, hour: int) -> Sequence[int]:
        """
         Get list of user_ids that should be notified on a specific hour.

        :param hour: The hour when user's should be notified.
        :return: List of user_ids.
        """
        get_stmt = (
            select(User.id)
            .where(User.notify_hours.contains([hour]))
        )
        result = await self.session.execute(get_stmt)
        return result.scalars().all()

    async def create_or_update(self, user_id: int, language: str, username: Optional[str] = None) -> User:
        """
        Creates or updates a new user in the database. Return user.
        :param user_id: The user's telegram ID.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        """
        insert_stmt = (
            insert(User)
            .values(
                id=user_id,
                username=username,
                language=language,
            )
            .on_conflict_do_update(
                index_elements=[User.id],
                set_=dict(
                    username=username,
                    language=language,
                    last_activity=utcnow(),
                ),
            )
            .returning(User)
        )

        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update_notify_hours(self, user_id: int, new_hours: List[int]) -> None:
        """
        Update user notify hours in the database.
        :param user_id: The user's telegram ID.
        :param new_hours: The new user's hours to notify.
        """
        update_stmt = (
            update(User)
            .where(User.id == user_id)
            .values(notify_hours=new_hours)
        )

        await self.session.execute(update_stmt)
        await self.session.commit()

    async def get_notify_hours(self, user_id: int) -> Optional[List[int]]:
        """
        Get user notify hours from the database.
        :param user_id: The user's telegram ID.
        :return: List with user notify hours or None.
        """
        select_stmt = (
            select(User.notify_hours)
            .where(User.id == user_id)
        )

        result = await self.session.execute(select_stmt)
        return result.scalar_one()

    async def get_last_activity(self, user_id: int) -> Optional[Activity]:
        """
        Get last created activity by user with `user_id`,
        :param user_id: The user's telegram ID in the database.
        :return: Last created user's activity.
        """
        get_stmt = (
            select(Activity)
            .where(Activity.user_id == user_id)
            .order_by(Activity.time.desc())
        )
        result = await self.session.scalars(get_stmt)
        return result.first()

    async def add_activities(self, user_id: int, activities: List[schemas.ActivityBase]) -> None:
        """
        Add list of new activities for user with `user_id`,
        :param user_id: The user's telegram ID in the database.
        :param activities: A list of new activities.
        """
        await self.bulk_add(
            objs=[Activity(user_id=user_id, **i.model_dump()) for i in activities]
        )

    async def update_tz_delta(self, user_id: int, tz_delta: int) -> None:
        """
        Update user time zone delta in the database.
        :param user_id: The user's telegram ID.
        :param tz_delta: The new user's time zone delta.
        """
        update_stmt = (
            update(User)
            .where(User.id == user_id)
            .values(time_zone_delta=tz_delta)
        )

        await self.session.execute(update_stmt)
        await self.session.commit()

    async def get_tz_delta(self, user_id: int) -> Optional[int]:
        """
        Get user notify hours from the database.
        :param user_id: The user's telegram ID.
        :return: User time zone delta or None.
        """
        select_stmt = (
            select(User.time_zone_delta)
            .where(User.id == user_id)
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
