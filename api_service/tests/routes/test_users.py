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

    result = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert result['success'] == True
    assert result['error'] is None
    assert result['data']['id'] == user_base.id
    assert result['data']['username'] == user_base.username
    assert result['data']['language'] == user_base.language

    db_user = await get_user_from_db(db_session, user_base.id)
    assert db_user.username == user_base.username
    assert db_user.language == user_base.language
    assert utcnow - timedelta(seconds=2) <= db_user.joined_at <= utcnow + timedelta(seconds=2)
    assert db_user.last_interaction_at == db_user.joined_at

    # Test updating
    user_base.language = 'ar'
    user_base.username = 'test_username'
    response = await async_client.put('/users', json=user_base.model_dump())

    new_result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert new_result['success'] == True
    assert new_result['error'] is None
    assert new_result['data']['id'] == user_base.id
    assert new_result['data']['username'] == user_base.username
    assert new_result['data']['language'] == user_base.language

    db_user = await get_user_from_db(db_session, user_base.id)
    assert db_user.last_interaction_at > db_user.joined_at
    assert db_user.username == user_base.username
    assert db_user.language == user_base.language


async def test_update_notifications_settings(async_client: AsyncClient, db_session: AsyncSession) -> None:
    # Test notify hours with time zone delta
    user = get_random_user_model(notify_hours=[1, 2, 3], time_zone_delta=-3)
    db_session.add(user)
    await db_session.commit()

    response = await async_client.put(f'/users/{user.id}/settings/notifications', json={'notify_hours': [2, 3, 4]})
    assert response.status_code == status.HTTP_200_OK
    expected_result = schemas.APIResponse(
        success=True, data=schemas.UserNotificationsSettingsOut(notify_hours=[23, 0, 1]), error=None
    )
    assert response.json() == expected_result.model_dump()

    db_user = await get_user_from_db(db_session, user.id)
    assert db_user.notify_hours == [23, 0, 1]

    # Test with `in UTC` arg
    response = await async_client.put(
        f'/users/{user.id}/settings/notifications',
        params={'is_in_utc': True},
        json={'notify_hours': [4, 5]},
    )
    assert response.status_code == status.HTTP_200_OK
    expected_result = schemas.APIResponse(
        success=True, data=schemas.UserNotificationsSettingsOut(notify_hours=[4, 5]), error=None
    )
    assert response.json() == expected_result.model_dump()

    db_user = await get_user_from_db(db_session, user.id)
    assert db_user.notify_hours == [4, 5]

    # Test empty notify hours
    response = await async_client.put(f'/users/{user.id}/settings/notifications', json={'notify_hours': []})
    assert response.status_code == status.HTTP_200_OK

    db_user = await get_user_from_db(db_session, user.id)
    assert len(db_user.notify_hours) == 0


async def test_update_notification_settings_incorrect_body(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model()
    db_session.add(user)
    await db_session.commit()

    async def try_update_notify_hours(notify_hours: list[int], error_msg: Optional[str] = None) -> None:
        response = await async_client.put(f'/users/{user.id}/settings/notifications', json={'notify_hours': notify_hours})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()['success'] is False
        assert response.json()['error']['code'] == 'VALIDATION_ERROR'
        if error_msg:
            assert error_msg in response.json()['error']['message']

        db_user = await get_user_from_db(db_session, user.id)
        assert db_user.notify_hours == user.notify_hours

    await try_update_notify_hours([-1, 5])
    await try_update_notify_hours([5, 24])
    await try_update_notify_hours([5, 5, 6], error_msg='Notify hours in the list must be unique.')


async def test_get_notification_settings(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model(notify_hours=[1, 2, 3])
    db_session.add(user)
    await db_session.commit()

    response = await async_client.get(f'/users/{user.id}/settings/notifications')
    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.UserNotificationsSettingsOut(notify_hours=[1, 2, 3])
    assert response.json() == schemas.APIResponse(success=True, data=expected_result, error=None).model_dump()


async def test_get_empty_notification_settings(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model(notify_hours=[])
    db_session.add(user)
    await db_session.commit()

    response = await async_client.get(f'/users/{user.id}/settings/notifications')
    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.UserNotificationsSettingsOut(notify_hours=[])
    assert response.json() == schemas.APIResponse(success=True, data=expected_result, error=None).model_dump()


async def test_get_latest_activity(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model()
    activity = get_random_activity_model(user_id=user.id)
    db_session.add_all([user, activity])
    await db_session.commit()

    response = await async_client.get(f'/users/{user.id}/activities/latest')
    assert response.status_code == status.HTTP_200_OK

    expected_data = schemas.ActivityOut(
        id=activity.id,
        utc_date=activity.utc_date,
        utc_hour=activity.utc_hour,
        type=activity.type,
    )
    assert response.json() == schemas.APIResponse(success=True, data=expected_data, error=None).model_dump(mode='json')


async def test_get_empty_latest_activity(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user = get_random_user_model()
    db_session.add(user)
    await db_session.commit()

    response = await async_client.get(f'/users/{user.id}/activities/latest')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == schemas.APIResponse(success=True, data=None, error=None).model_dump()


async def test_get_closet_missing_slots_to_set_activities(async_client: AsyncClient, db_session: AsyncSession) -> None:
    # We mock utc_now with minutes and seconds to check that we don't have it in the result
    fake_current_datetime = datetime(year=2025, month=4, day=15, hour=12, minute=30, second=5)
    current_clear_datetime = datetime_to_clear_format(fake_current_datetime)

    user = get_random_user_model()
    activity = get_random_activity_model(user_id=user.id, utc_date=date(year=2025, month=4, day=15), utc_hour=8)
    db_session.add_all([user, activity])
    await db_session.commit()

    with freeze_time(fake_current_datetime):
        response = await async_client.get(f'/users/{user.id}/activities/missing_slots/closest')
    assert response.status_code == status.HTTP_200_OK

    expected_data = schemas.MissingActivitySlotsOut(
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
    assert response.json()['success'] is True
    assert response.json()['data']['date_range'] == expected_data.date_range.model_dump(mode='json')
    assert response.json() == schemas.APIResponse(success=True, data=expected_data, error=None).model_dump(mode='json')


async def test_get_closets_missing_slots_for_newbie(async_client: AsyncClient, db_session: AsyncSession) -> None:
    fake_current_datetime = datetime(year=2025, month=4, day=15, hour=2, minute=30, second=8)
    current_clear_datetime = datetime_to_clear_format(fake_current_datetime)

    user = get_random_user_model()
    db_session.add(user)
    await db_session.commit()

    with freeze_time(fake_current_datetime):
        response = await async_client.get(f'/users/{user.id}/activities/missing_slots/closest')
    assert response.status_code == status.HTTP_200_OK

    expected_date_range = schemas.DateRange(
        from_date=current_clear_datetime - timedelta(hours=6),
        to_date=current_clear_datetime - timedelta(hours=1)
    )
    expected_data = schemas.MissingActivitySlotsOut(
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
    assert response.json()['success'] is True
    assert len(response.json()['data']['missing_slots']) == expected_data.total_missing
    assert response.json() == schemas.APIResponse(success=True, data=expected_data, error=None).model_dump(mode='json')


async def test_get_empty_closets_missing_slots(async_client: AsyncClient, db_session: AsyncSession) -> None:
    fake_current_datetime = datetime(year=2025, month=4, day=15, hour=12, minute=30, second=8)

    user = get_random_user_model()
    activity = get_random_activity_model(user_id=user.id, utc_date=date(year=2025, month=4, day=15), utc_hour=11)
    db_session.add_all([user, activity])
    await db_session.commit()

    with freeze_time(fake_current_datetime):
        response = await async_client.get(f'/users/{user.id}/activities/missing_slots/closest')
    assert response.status_code == status.HTTP_200_OK

    expected_data = schemas.MissingActivitySlotsOut(
        has_missing_slots=False,
        date_range=None,
        missing_slots=None,
        total_missing=0
    )
    assert response.json() == schemas.APIResponse(success=True, data=expected_data, error=None).model_dump()
