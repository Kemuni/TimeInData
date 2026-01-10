from typing import Optional, List, Sequence, Tuple

from sqlalchemy import update, select, func, Row
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import desc

from app import schemas
from app.database.func import db_utcnow
from app.database.models import User, Activity, Base, ActivityTypes


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
         Get a list of user_ids that should be notified on a specific hour.

        :param hour: The hour when user should be notified.
        :return: List of user_ids.
        """
        get_stmt = (
            select(User.id)
            .where(User.notify_utc_hours.contains([hour]))
        )
        result = await self.session.execute(get_stmt)
        return result.scalars().all()

    async def create_or_update(self, user_id: int, language: str, username: Optional[str] = None) -> Tuple[User, bool]:
        """
        Creates or updates a new user in the database. Return user and is_created bool.
        :param user_id: The user's telegram ID.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: The User model and bool is_created, True if it is a new user, otherwise False.
        """
        is_created_column = (User.joined_at == User.last_interaction_at).label("is_created")
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
                    last_interaction_at=db_utcnow(),
                ),
            )
            .returning(
                User,
                is_created_column
            )
        )

        result = await self.session.execute(insert_stmt)
        await self.session.commit()

        user, is_created = result.one()
        await self.session.refresh(user)

        return user, is_created

    async def update_notify_utc_hours(self, user_id: int, new_hours: List[int]) -> None:
        """
        Update user notifies hours in the database.
        :param user_id: The user's telegram ID.
        :param new_hours: The new user's utc hours to notify.
        """
        update_stmt = (
            update(User)
            .where(User.id == user_id)
            .values(notify_utc_hours=new_hours)
        )

        await self.session.execute(update_stmt)
        await self.session.commit()

    async def get_notify_utc_hours(self, user_id: int) -> Optional[List[int]]:
        """
        Get user notifies UTC hours from the database.
        :param user_id: The user's telegram ID.
        :return: List with user notify hours or None.
        """
        select_stmt = (
            select(User.notify_utc_hours)
            .where(User.id == user_id)
        )

        result = await self.session.execute(select_stmt)
        return result.scalar_one()

    async def get_latest_activity(self, user_id: int) -> Optional[Activity]:
        """
        Get last created activity by user with `user_id`,
        :param user_id: The user's telegram ID in the database.
        :return: Last created user's activity.
        """
        get_stmt = (
            select(Activity)
            .where(Activity.user_id == user_id)
            .order_by(desc(Activity.utc_date), desc(Activity.utc_hour))
            .limit(1)
        )
        result = await self.session.execute(get_stmt)
        return result.scalar_one_or_none()

    async def add_activities(self, user_id: int, activities: List[schemas.ActivityBase]) -> None:
        """
        Add a list of new activities for user with `user_id`,
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

    async def get_activities_summary(self, user_id: int) -> Sequence[Row[tuple[str, int]]]:
        """
        Get user's activities summary like [Activity, amount_of_hours].

        :param user_id: The user's telegram ID.
        :return: User's activities summary.
        """
        select_stmt = (
            select(Activity.type, func.count(Activity.id))
            .where(Activity.user_id == user_id)
            .group_by(Activity.type)
        )

        result = await self.session.execute(select_stmt)
        return result.all()


class DatabaseRepo(BaseRepo):
    """
    Repository for handling database operations. This class holds all the repositories for the database models.
    """

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)
