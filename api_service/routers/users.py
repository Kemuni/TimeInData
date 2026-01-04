from datetime import datetime, timedelta
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, status, Body, HTTPException, Response
from pydantic import Field
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

import schemas
from database.repositories import DatabaseRepo
from dependencies import get_db
from loguru import  logger

from utils.utcnow import utcnow

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/to_notify')
async def get_users_to_notify(db: DatabaseRepo = Depends(get_db)) -> schemas.UsersToNotifyOut:
    """ Get users, which a needed to be notified (set activities) in the current UTC hour. """
    user_ids = await db.users.get_ids_to_notify(utcnow().hour) or []
    return schemas.UsersToNotifyOut(user_ids=user_ids)


@router.put('', response_model=schemas.UserOut)
async def create_or_update(user: schemas.UserBase, db: DatabaseRepo = Depends(get_db)):
    """ Create or update user in the database. """
    db_user, is_created = await db.users.create_or_update(**user.model_dump(by_alias=True))
    return JSONResponse(
        status_code=status.HTTP_201_CREATED if is_created else status.HTTP_200_OK,
        content=schemas.UserOut.model_validate(db_user, from_attributes=True).model_dump(by_alias=True),
    )


@router.put('/{user_id}/notify_hours')
async def update_notify_hours(
        user_id: schemas.TelegramUserId,
        hours_data: schemas.UserNotifyHoursIn,
        db: DatabaseRepo = Depends(get_db)
) -> Response:
    """  Update user hours to notify in the database. """
    await db.users.update_notify_hours(user_id, hours_data.notify_hours)
    return Response(status_code=status.HTTP_200_OK, content="User's notify hours has been updated.")


@router.get('/{user_id}/notify_hours')
async def get_notify_hours(
        user_id: schemas.TelegramUserId,
        db: DatabaseRepo = Depends(get_db)
) -> schemas.UserNotifyHoursOut:
    """ Get user hours to notify from the database. """
    notify_hours = await db.users.get_notify_hours(user_id) or []
    return schemas.UserNotifyHoursOut(notify_hours=notify_hours)


@router.get('/{user_id}/activities/last')
async def get_last_activity(
        user_id: schemas.TelegramUserId,
        db: DatabaseRepo = Depends(get_db)
) -> Optional[schemas.ActivityOut]:
    """  Get last created activity by user with `user_id`. """
    last_activity = await db.users.get_last_activity(user_id)
    return schemas.ActivityOut.model_validate(last_activity) if last_activity else None


@router.get(
    '/{user_id}/activities/time_interval',
    description='''
    Get the time interval to set activities for user with `user_id`. For newbie users, we display fewer hours.
    For example `["2025.02.01 11:00", "2025.02.02 13:00"]` result means that you have to set activities in 
    11:00, 12:00 and 13:00 time. So, **from_date and to_date are inclusive** in the interval.
    '''
)
async def get_time_interval_to_set_activities(
        user_id: schemas.TelegramUserId,
        max_hours_delta: Optional[int] = 24,
        newbie_hours_delta: Optional[int] = 6,
        db: DatabaseRepo = Depends(get_db),
) -> schemas.TimeIntervalResponse:
    """
    Get the time interval to set activities for user with `user_id`. For newbie users, we display fewer hours.
    For example [2025.02.01 11:00, 2025.02.02 13:00] result means that you have to set 11:00, 12:00, 13:00 activities.

    :param user_id: The user's telegram ID.
    :param max_hours_delta: The maximum hours delta in the interval.
    :param newbie_hours_delta: The hour delta in the interval for newbie user.
    :param db: The database repository.
    :return: Time interval to set activities.
    """
    last_activity = await db.users.get_last_activity(user_id)
    utc_now = utcnow()
    is_newbie_user = last_activity is None

    if is_newbie_user:
        max_hours_delta = newbie_hours_delta
        from_date = datetime(utc_now.year, utc_now.month, utc_now.day, utc_now.hour) - timedelta(hours=max_hours_delta)
    else:
        from_date = last_activity.start_datetime_utc + timedelta(hours=1)

    to_date = min(
        from_date + timedelta(hours=max_hours_delta),
        # if now is 22:33, we can set activity only to 21:00, so we subtract 1 hour
        datetime(utc_now.year, utc_now.month, utc_now.day, utc_now.hour - 1)
    )
    has_items_to_fill = (utc_now - from_date) > timedelta(hours=1)

    if has_items_to_fill:
        return schemas.TimeIntervalResponse(
            has_items_to_fill=has_items_to_fill,
            is_newbie_user=is_newbie_user,
            interval= schemas.TimeInterval(
                from_date=from_date,
                to_date=to_date,
            ),
        )
    return schemas.TimeIntervalResponse(
        has_items_to_fill=has_items_to_fill,
        is_newbie_user=is_newbie_user,
        interval=None,
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


@router.put('/{user_id}/tz_delta')
async def update_time_zone_delta(
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


@router.get('/{user_id}/tz_delta')
async def get_time_zone_delta(
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
