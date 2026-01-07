from datetime import datetime, timedelta, UTC, date
from typing import Optional

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from tests.utils.activity import get_random_activity_model
from tests.utils.user import get_random_user_model, get_random_user_base_schema, get_user_from_db
from tests.utils.utils import datetime_to_clear_format
from freezegun import freeze_time


async def test_create_or_update(async_client: AsyncClient, db_session: AsyncSession) -> None:
    # Test creation
    user_base = get_random_user_base_schema()
    utcnow = datetime.now(UTC).replace(tzinfo=None)
    response = await async_client.put('/users', json=user_base.model_dump())

    assert response.status_code == status.HTTP_201_CREATED

    db_user = await get_user_from_db(db_session, user_base.id)
    assert db_user.username == user_base.username
    assert db_user.language == user_base.language
    assert utcnow - timedelta(seconds=2) <= db_user.joined_at <= utcnow + timedelta(seconds=2)
    assert db_user.last_activity == db_user.joined_at

    # Test updating
    user_base.language = 'ar'
    user_base.username = 'test_username'
    response = await async_client.put('/users', json=user_base.model_dump())

    assert response.status_code == status.HTTP_200_OK

    db_user = await get_user_from_db(db_session, user_base.id)
    assert db_user.last_activity > db_user.joined_at
    assert db_user.username == user_base.username
    assert db_user.language == user_base.language


async def test_get_users_to_notify(async_client: AsyncClient, db_session: AsyncSession) -> None:
    # Test empty result
    response = await async_client.get('/users/to_notify')

    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.UsersToNotifyOut(user_ids=[])
    assert response.json() == expected_result.model_dump()

    # Test non-empty result
    user1 = get_random_user_model(notify_hours=[1, 2, 3])
    user2 = get_random_user_model(notify_hours=[3, 4, 5])
    user3 = get_random_user_model(notify_hours=[5, 6, 7])
    db_session.add_all([user1, user2, user3])
    await db_session.commit()

    fixed_datetime = datetime(year=2025, month=4, day=15, hour=3, minute=0, second=0)
    with freeze_time(fixed_datetime):
        response = await async_client.get('/users/to_notify')

    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.UsersToNotifyOut(user_ids=[user1.id, user2.id])
    assert response.json() == expected_result.model_dump()


async def test_update_notify_hours(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model(notify_hours=[1, 2, 3])
    db_session.add(user)
    await db_session.commit()

    response = await async_client.put(f'/users/{user.id}/notify_hours', json={'notify_hours': [4, 5, 6]})
    assert response.status_code == status.HTTP_200_OK
    assert response.text == "User's notify hours has been updated."

    db_user = await get_user_from_db(db_session, user.id)
    assert db_user.notify_hours == [4, 5, 6]

    response = await async_client.put(f'/users/{user.id}/notify_hours', json={'notify_hours': []})
    assert response.status_code == status.HTTP_200_OK

    db_user = await get_user_from_db(db_session, user.id)
    assert len(db_user.notify_hours) == 0


async def test_update_notify_hours_incorrect_body(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model()
    db_session.add(user)
    await db_session.commit()

    async def try_update_notify_hours(notify_hours: list[int], error_msg: Optional[str] = None) -> None:
        response = await async_client.put(f'/users/{user.id}/notify_hours', json={'notify_hours': notify_hours})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        if error_msg:
            assert response.json()['detail'][0]['msg'] == error_msg

        db_user = await get_user_from_db(db_session, user.id)
        assert db_user.notify_hours == user.notify_hours

    await try_update_notify_hours([-1, 5])
    await try_update_notify_hours([5, 24])
    await try_update_notify_hours([5, 5, 6], error_msg='Notify hours in the list must be unique.')


async def test_get_notify_hours(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model(notify_hours=[1, 2, 3])
    db_session.add(user)
    await db_session.commit()

    response = await async_client.get(f'/users/{user.id}/notify_hours')
    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.UserNotifyHoursOut(notify_hours=[1, 2, 3])
    assert response.json() == expected_result.model_dump()


async def test_get_empty_notify_hours(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model(notify_hours=[])
    db_session.add(user)
    await db_session.commit()

    response = await async_client.get(f'/users/{user.id}/notify_hours')
    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.UserNotifyHoursOut(notify_hours=[])
    assert response.json() == expected_result.model_dump()


async def test_get_last_activity(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model()
    activity = get_random_activity_model(user_id=user.id)
    db_session.add_all([user, activity])
    await db_session.commit()

    response = await async_client.get(f'/users/{user.id}/activities/last')
    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.ActivityOut(
        id=activity.id,
        utc_date=activity.utc_date,
        utc_hour=activity.utc_hour,
        type=activity.type,
    )
    assert response.json() == expected_result.model_dump(mode='json')


async def test_get_empty_last_activity(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model()
    db_session.add(user)
    await db_session.commit()

    response = await async_client.get(f'/users/{user.id}/activities/last')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is None


async def test_get_closet_missing_slots_to_set_activities(async_client: AsyncClient, db_session: AsyncSession) -> None:
    # We mock utc_now with minutes and seconds to check that we don't have it in the result
    fake_current_datetime = datetime(year=2025, month=4, day=15, hour=12, minute=30, second=5)
    current_clear_datetime = datetime_to_clear_format(fake_current_datetime)

    user = get_random_user_model()
    activity = get_random_activity_model(user_id=user.id, utc_date=date(year=2025, month=4, day=15), utc_hour=8)
    db_session.add_all([user, activity])
    await db_session.commit()

    with freeze_time(fake_current_datetime):
        response = await async_client.get(f'/users/{user.id}/activities/closest_missing_slots')
    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.MissingActivitySlotsOut(
        has_missing_slots=True,
        date_range=schemas.DateRange(
            from_date=activity.start_datetime_utc + timedelta(hours=1),
            to_date=current_clear_datetime - timedelta(hours=1)
        ),
        missing_slots=[
            schemas.MissingActivitySlot(utc_date=activity.utc_date, utc_hour=activity.utc_hour + 1),
            schemas.MissingActivitySlot(utc_date=activity.utc_date, utc_hour=activity.utc_hour + 2),
            schemas.MissingActivitySlot(utc_date=activity.utc_date, utc_hour=activity.utc_hour + 3),
        ],
        total_missing=3
    )
    assert response.json()['date_range'] == expected_result.date_range.model_dump(mode='json')
    assert response.json() == expected_result.model_dump(mode='json')


async def test_get_closets_missing_slots_for_newbie(async_client: AsyncClient, db_session: AsyncSession) -> None:
    fake_current_datetime = datetime(year=2025, month=4, day=15, hour=2, minute=30, second=8)
    current_clear_datetime = datetime_to_clear_format(fake_current_datetime)

    user = get_random_user_model()
    db_session.add(user)
    await db_session.commit()

    with freeze_time(fake_current_datetime):
        response = await async_client.get(f'/users/{user.id}/activities/closest_missing_slots')
    assert response.status_code == status.HTTP_200_OK

    expected_date_range = schemas.DateRange(
        from_date=current_clear_datetime - timedelta(hours=6),
        to_date=current_clear_datetime - timedelta(hours=1)
    )
    expected_result = schemas.MissingActivitySlotsOut(
        has_missing_slots=True,
        date_range=expected_date_range,
        missing_slots=[
            schemas.MissingActivitySlot(
                utc_date=expected_date_range.from_date.date() + timedelta(days=(expected_date_range.from_date.hour + i) // 24),
                utc_hour=(expected_date_range.from_date.hour + i) % 24
            )
            for i in range(6)
        ],
        total_missing=6
    )
    assert len(response.json()['missing_slots']) == expected_result.total_missing
    assert response.json() == expected_result.model_dump(mode='json')


async def test_get_empty_closets_missing_slots(async_client: AsyncClient, db_session: AsyncSession) -> None:
    fake_current_datetime = datetime(year=2025, month=4, day=15, hour=12, minute=30, second=8)

    user = get_random_user_model()
    activity = get_random_activity_model(user_id=user.id, utc_date=date(year=2025, month=4, day=15), utc_hour=11)
    db_session.add_all([user, activity])
    await db_session.commit()

    with freeze_time(fake_current_datetime):
        response = await async_client.get(f'/users/{user.id}/activities/closest_missing_slots')
    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.MissingActivitySlotsOut(
        has_missing_slots=False,
        date_range=None,
        missing_slots=None,
        total_missing=0
    )
    assert response.json() == expected_result.model_dump(mode='json')
