from datetime import timedelta
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, status, Body, HTTPException, Response
from loguru import logger
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from app import schemas
from app.database.repositories import DatabaseRepo
from app.dependencies import get_db
from app.services.ActivityTrackerService import ActivityTrackerService
from app.utils.utcnow import utcnow

router = APIRouter(prefix='/users', tags=['users'])


@router.put('', response_model=schemas.UserOut)
async def create_or_update(user: schemas.UserBase, db: DatabaseRepo = Depends(get_db)):
    """ Create or update user in the database. """
    db_user, is_created = await db.users.create_or_update(**user.model_dump(by_alias=True))
    return JSONResponse(
        status_code=status.HTTP_201_CREATED if is_created else status.HTTP_200_OK,
        content=schemas.UserOut.model_validate(db_user, from_attributes=True).model_dump(by_alias=True),
    )


@router.put('/{user_id}/settings/notifications')
async def update_notifications_settings(
        user_id: schemas.TelegramUserId,
        hours_data: schemas.UserNotificationsSettingsIn,
        db: DatabaseRepo = Depends(get_db)
) -> Response:
    """  Update user hours to notify in the database. """
    await db.users.update_notify_hours(user_id, hours_data.notify_hours)
    return Response(status_code=status.HTTP_200_OK, content="User's notify hours has been updated.")


@router.get('/{user_id}/settings/notifications')
async def get_notifications_settings(
        user_id: schemas.TelegramUserId,
        db: DatabaseRepo = Depends(get_db)
) -> schemas.UserNotificationsSettingsOut:
    """ Get user hours to notify from the database. """
    notify_hours = await db.users.get_notify_hours(user_id) or []
    return schemas.UserNotificationsSettingsOut(notify_hours=notify_hours)


@router.get('/{user_id}/activities/latest')
async def get_latest_activity(
        user_id: schemas.TelegramUserId,
        db: DatabaseRepo = Depends(get_db)
) -> Optional[schemas.ActivityOut]:
    """  Get the latest created activity by user with `user_id`. """
    latest_activity = await db.users.get_latest_activity(user_id)
    return schemas.ActivityOut.model_validate(latest_activity) if latest_activity else None


@router.get(
    '/{user_id}/activities/missing_slots/closest',
    description='''
    Get the closest missing slots to set activities for user with `user_id`. For newbie users, we display fewer hours.
    '''
)
async def get_activities_closest_missing_slots(
        user_id: schemas.TelegramUserId,
        max_missing_slots: Optional[int] = 24,
        db: DatabaseRepo = Depends(get_db),
) -> schemas.MissingActivitySlotsOut:
    """
    Get the closest missing slots to set activities for user with `user_id`. For newbie users, we display fewer
    slots (6 slots).

    :param user_id: The user's telegram ID.
    :param max_missing_slots: The maximum missing slots to display.
    :param db: The database repository.
    :return: Data about missing slots to set activities.
    """
    # Get missing slots date range
    activity_tracker = ActivityTrackerService(db, user_id)
    date_range = await activity_tracker.get_closest_missing_slots_date_range(max_missing_slots)
    if date_range is None:
        return schemas.MissingActivitySlotsOut(
            has_missing_slots=False, date_range=None, missing_slots=None, total_missing=0,
        )
    from_date, to_date = date_range.from_date, date_range.to_date

    # Calculating slots
    missing_slots = [
        schemas.MissingActivitySlot(
            utc_date=(from_date.date() + timedelta(days=((from_date.hour + i) // 24))),
            utc_hour=(from_date.hour + i) % 24
        )
        for i in range(date_range.total_hours)
    ]

    return schemas.MissingActivitySlotsOut(
        has_missing_slots=True,
        date_range=schemas.DateRange(from_date=from_date, to_date=to_date),
        missing_slots=missing_slots,
        total_missing=date_range.total_hours,
    )


@router.post(
    '/{user_id}/activities',
    description='Creating new activities in UTC time.',
    status_code=status.HTTP_201_CREATED,
)
async def add_activities(
        user_id: schemas.TelegramUserId,
        activities: Annotated[List[schemas.ActivityIn], Body(embed=True)],
        db: DatabaseRepo = Depends(get_db)
) -> Response:
    """ Add a list of new activities for user with `user_id`. """
    utcnow_timestamp = utcnow().timestamp()
    for activity in activities:
        if activity.timestamp() > utcnow_timestamp:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail=f"Incorrect activity time. {activity.utc_date} {activity.utc_hour}:00 is invalid.")

    try:
        await db.users.add_activities(user_id, activities)
    except IntegrityError as exc:
        logger.error(f'Get activity which time is already exist. IntegrityError: {exc}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Incorrect activity time. The time in one of the activities is already exists.")

    return Response(status_code=status.HTTP_201_CREATED, content="Activities have been added")


@router.put('/{user_id}/settings/timezone')
async def update_user_time_zone(
        user_id: schemas.TelegramUserId,
        tz_delta: Annotated[
            schemas.TzDeltaNumber, 
            Body(embed=True),
        ],
        db: DatabaseRepo = Depends(get_db)
) -> Response:
    """ Update user time zone delta in the database. User time = utc_hour + time_zone_delta (tz_delta). """
    await db.users.update_tz_delta(user_id, tz_delta)
    return Response(status_code=status.HTTP_200_OK, content="User's time zone delta has been updated")


@router.get('/{user_id}/settings/timezone')
async def get_user_time_zone(
        user_id: schemas.TelegramUserId,
        db: DatabaseRepo = Depends(get_db)
) -> schemas.UserTimeZoneDeltaOut:
    """ Get user time zone delta from the database. """
    tz_delta = await db.users.get_tz_delta(user_id) or 0
    return schemas.UserTimeZoneDeltaOut(tz_delta=tz_delta)


@router.get('/{user_id}/activities/summary')
async def get_activity_summary(
        user_id: schemas.TelegramUserId,
        db: DatabaseRepo = Depends(get_db)
) -> schemas.UserActivitiesSummaryOut:
    """ Get activity summary for user with `user_id`. """
    summary = await db.users.get_activities_summary(user_id)
    return schemas.UserActivitiesSummaryOut(
        data=[
            schemas.UserActivitySummary(type_id=activity_type, type_name=activity_type.name, amount=amount)
            for activity_type, amount in summary
        ]
    )
