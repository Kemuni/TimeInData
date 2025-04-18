from collections import Counter
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Activity
from database.repositories import UserRepo
from tests.utils.activity import get_random_activity_model, get_random_activity_base
from tests.utils.user import get_random_user_model, get_random_telegram_id, get_user_from_db
from tests.utils.utils import get_random_lower_string, get_random_datetime

pytestmark = pytest.mark.asyncio


async def test_get_ids_to_notify(db_session: AsyncSession) -> None:
    user1 = get_random_user_model(notify_hours=[1, 2, 3])
    user2 = get_random_user_model(notify_hours=[3, 4, 5])
    user3 = get_random_user_model(notify_hours=[5, 6, 7])

    db_session.add_all([user1, user2, user3])
    await db_session.commit()

    expected_result = [user1.id, user2.id]

    result = await UserRepo(session=db_session).get_ids_to_notify(3)

    assert result == expected_result


async def test_get_ids_to_notify_empty(db_session: AsyncSession) -> None:
    db_session.add_all([
        get_random_user_model(notify_hours=[1, 2, 3]),
        get_random_user_model(notify_hours=[3, 4, 5])
    ])
    await db_session.commit()

    result = await UserRepo(session=db_session).get_ids_to_notify(6)

    assert result == []


async def test_user_create_or_update(db_session: AsyncSession) -> None:
    repo = UserRepo(session=db_session)

    # Test create
    user_schema = get_random_user_model(
        _id=get_random_telegram_id(),
        language="en",
        username=get_random_lower_string(),
        notify_hours=[],
        time_zone_delta=0,
    )

    utc_now = datetime.utcnow()
    user, is_created = await repo.create_or_update(
        user_id=user_schema.id, language=user_schema.language, username=user_schema.username
    )

    assert is_created is True
    assert user.id == user_schema.id
    assert user.language == user_schema.language
    assert user.username == user_schema.username
    assert user.notify_hours is None
    assert user.time_zone_delta == 0
    assert utc_now - timedelta(seconds=2) <= user.joined_at <= utc_now + timedelta(seconds=2)
    assert user.joined_at == user.last_activity

    # Test update
    user_schema.username = get_random_lower_string()
    user_schema.language = "ru"
    utc_now = datetime.utcnow()
    user, is_created = await repo.create_or_update(
        user_id=user_schema.id, language=user_schema.language, username=user_schema.username
    )

    assert is_created is False
    assert user.id == user_schema.id
    assert user.language == user_schema.language
    assert user.username == user_schema.username
    assert user.notify_hours is None
    assert user.time_zone_delta == 0
    assert user.joined_at != user.last_activity
    assert utc_now - timedelta(seconds=2) <= user.last_activity <= utc_now + timedelta(seconds=2)


async def test_update_notify_hours(db_session: AsyncSession) -> None:
    user = get_random_user_model(notify_hours=[1, 2, 3])

    db_session.add(user)
    await db_session.commit()

    new_hours = [4, 5, 6]
    await UserRepo(session=db_session).update_notify_hours(user.id, new_hours)

    db_user = await get_user_from_db(db_session, user.id)

    assert db_user.notify_hours == new_hours


async def test_get_notify_hours(db_session: AsyncSession) -> None:
    user1 = get_random_user_model(notify_hours=[1, 4, 3])
    user2 = get_random_user_model(notify_hours=[])

    db_session.add_all([user1, user2])
    await db_session.commit()

    notify_hours = await UserRepo(session=db_session).get_notify_hours(user1.id)
    assert notify_hours == user1.notify_hours

    notify_hours = await UserRepo(session=db_session).get_notify_hours(user2.id)
    assert notify_hours is None or notify_hours == []


async def test_get_last_activity(db_session: AsyncSession) -> None:
    user = get_random_user_model()

    db_session.add(user)
    await db_session.commit()

    user_repo = UserRepo(session=db_session)

    last_activity = await user_repo.get_last_activity(user.id)
    assert last_activity is None

    activity1 = get_random_activity_model(user_id=user.id)
    activity2 = get_random_activity_model(
        user_id=user.id,
        time=get_random_datetime(to_date=activity1.time) - timedelta(hours=1),
    )
    db_session.add_all([activity1, activity2])
    await db_session.commit()

    last_activity = await user_repo.get_last_activity(user.id)
    assert last_activity.id == activity1.id
    assert last_activity.user_id == activity1.user_id
    assert last_activity.time == activity1.time
    assert last_activity.type == activity1.type


async def test_add_activities(db_session: AsyncSession) -> None:
    user = get_random_user_model()
    db_session.add(user)
    await db_session.commit()

    activities = [get_random_activity_base() for _ in range(4)]

    await UserRepo(session=db_session).add_activities(user_id=user.id, activities=activities)

    result = await db_session.execute(select(Activity).where(Activity.user_id == user.id))
    db_activities = result.scalars().all()

    assert len(db_activities) == len(activities)
    assert all(db_activity.user_id == user.id for db_activity in db_activities)

    db_activities_types_counter = Counter(activity.type for activity in db_activities)
    activities_types_counter = Counter(activity.type for activity in activities)

    assert db_activities_types_counter == activities_types_counter


async def test_update_tz_delta(db_session: AsyncSession) -> None:
    user = get_random_user_model(time_zone_delta=0)
    db_session.add(user)
    await db_session.commit()

    await UserRepo(session=db_session).update_tz_delta(user.id, 1)

    db_user = await get_user_from_db(db_session, user.id)
    assert db_user.time_zone_delta == 1


async def test_get_tz_delta(db_session: AsyncSession) -> None:
    user = get_random_user_model(time_zone_delta=2)
    db_session.add(user)
    await db_session.commit()

    tz_delta = await UserRepo(session=db_session).get_tz_delta(user.id)

    assert user.time_zone_delta == tz_delta


async def test_get_activities_summary(db_session: AsyncSession) -> None:
    user = get_random_user_model()
    db_session.add(user)
    await db_session.commit()

    activities = [get_random_activity_model(user_id=user.id) for _ in range(10)]
    db_session.add_all(activities)
    await db_session.commit()

    summary = await UserRepo(session=db_session).get_activities_summary(user.id)

    activities_types_counter = Counter(activity.type for activity in activities)

    assert len(summary) == len(activities_types_counter)

    for activity_type, amount in summary:
        assert activities_types_counter[activity_type] == amount
