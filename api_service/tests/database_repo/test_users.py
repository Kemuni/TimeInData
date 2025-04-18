from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import UserRepo
from tests.utils.user import get_random_user_model, get_random_telegram_id
from tests.utils.utils import get_random_lower_string


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
    user1 = get_random_user_model(notify_hours=[1, 2, 3])
    user2 = get_random_user_model(notify_hours=[3, 4, 5])

    db_session.add_all([user1, user2])
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
