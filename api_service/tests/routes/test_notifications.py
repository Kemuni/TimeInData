from datetime import datetime

from fastapi import status
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from tests.utils.user import get_random_user_model


async def test_get_set_activities_reminder_pending_notifications(async_client: AsyncClient, db_session: AsyncSession) -> None:
    # Test empty result
    response = await async_client.get('/notifications/set_activities_reminder/pending')

    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.PendingNotificationsOut(
        user_ids=[], type='set_activities_reminder', total_notifications=0,
    )
    assert response.json() == schemas.APIResponse(success=True, data=expected_result, error=None).model_dump()

    # Test non-empty result
    user1 = get_random_user_model(notify_utc_hours=[1, 2, 3])
    user2 = get_random_user_model(notify_utc_hours=[3, 4, 5])
    user3 = get_random_user_model(notify_utc_hours=[5, 6, 7])
    db_session.add_all([user1, user2, user3])
    await db_session.commit()

    fixed_datetime = datetime(year=2025, month=4, day=15, hour=3, minute=0, second=0)
    with freeze_time(fixed_datetime):
        response = await async_client.get('/notifications/set_activities_reminder/pending')

    assert response.status_code == status.HTTP_200_OK

    expected_result = schemas.PendingNotificationsOut(
        user_ids=[user1.id, user2.id],
        type='set_activities_reminder',
        total_notifications=2,
    )

    assert response.json() == schemas.APIResponse(success=True, data=expected_result, error=None).model_dump()
