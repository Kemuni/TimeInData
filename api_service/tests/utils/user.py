from datetime import datetime
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from tests.utils.utils import get_random_lower_string, get_random_datetime, get_random_number


def get_random_telegram_id() -> int:
    return get_random_number(100_000_000, 999_999_999)


def get_random_user_model(
        _id: Optional[int] = None,
        username: Optional[str] = None,
        language: Optional[str] = None,
        joined_at: Optional[datetime] = None,
        last_activity: Optional[datetime] = None,
        notify_hours: Optional[List[int]] = None,
        time_zone_delta: Optional[int] = None
):
    """ Create random model of `User`. NO OBJECT CREATION IN DATABASE. """
    joined_at = joined_at or get_random_datetime()
    last_activity = last_activity or get_random_datetime(from_date=joined_at)
    if notify_hours is None:
        notify_hours = list(range(get_random_number(min_num=0, max_num=24)))

    return User(
        id=_id or get_random_telegram_id(),
        username=username or get_random_lower_string(length=32),
        language=language or "en",
        joined_at=joined_at,
        last_activity=last_activity,
        notify_hours=notify_hours,
        time_zone_delta=time_zone_delta or get_random_number(min_num=-6, max_num=6)
    )


async def get_user_from_db(db_session: AsyncSession, user_id: int) -> User:
    """ Get User model from database by id. """
    select_stmt = select(User).where(User.id == user_id)
    result = await db_session.execute(select_stmt)
    return result.scalars().first()
