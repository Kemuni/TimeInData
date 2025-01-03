from datetime import datetime
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, status, Body, HTTPException, Response
from starlette.responses import JSONResponse

import schemas
from database.repositories import DatabaseRepo
from dependencies import get_db

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/to_notify')
async def get_users_to_notify(db: DatabaseRepo = Depends(get_db)) -> schemas.UsersToNotifyOut:
    user_ids = await db.users.get_ids_to_notify(datetime.utcnow().hour) or []
    return schemas.UsersToNotifyOut(user_ids=user_ids)


@router.put('', response_model=schemas.UserOut)
async def create_or_update(user: schemas.UserBase, db: DatabaseRepo = Depends(get_db)):
    db_user, is_created = await db.users.create_or_update(**user.model_dump(by_alias=True))
    return JSONResponse(
        status_code=status.HTTP_201_CREATED if is_created else status.HTTP_200_OK,
        content=schemas.UserOut.model_validate(db_user, from_attributes=True).model_dump(by_alias=True),
    )


@router.put('/{user_id}/notify_hours')
async def update_notify_hours(
        user_id: schemas.TelegramUserId,
        notify_hours: Annotated[List[schemas.HourNumber], Body(embed=True)],
        db: DatabaseRepo = Depends(get_db)
) -> Response:
    await db.users.update_notify_hours(user_id, notify_hours)
    return Response(status_code=status.HTTP_200_OK, content="User's notify hours has been updated")


@router.get('/{user_id}/notify_hours')
async def get_notify_hours(user_id: schemas.TelegramUserId, db: DatabaseRepo = Depends(get_db)) -> schemas.UserNotifyHoursOut:
    notify_hours = await db.users.get_notify_hours(user_id) or []
    return schemas.UserNotifyHoursOut(notify_hours=notify_hours)


@router.get('/{user_id}/activities/last')
async def get_last_activity(user_id: schemas.TelegramUserId, db: DatabaseRepo = Depends(get_db)) -> Optional[schemas.LastActivityOut]:
    last_activity = await db.users.get_last_activity(user_id)
    return schemas.LastActivityOut.model_validate(last_activity) if last_activity else None


@router.post(
    '/{user_id}/activities',
    description='Creating new activities in UTC time.',
    status_code=status.HTTP_201_CREATED,
)
async def add_activities(
        user_id: schemas.TelegramUserId,
        activities: Annotated[List[schemas.ActivityBase], Body(embed=True)],
        db: DatabaseRepo = Depends(get_db)
):
    for activity in activities:
        if activity.time > datetime.now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Incorrect activity time. {activity.time} is invalid")
    await db.users.add_activities(user_id, activities)


@router.put('/{user_id}/tz_delta')
async def update_time_zone_delta(
        user_id: schemas.TelegramUserId,
        tz_delta: Annotated[
            schemas.TzDeltaNumber, 
            Body(embed=True),
        ],
        db: DatabaseRepo = Depends(get_db)
) -> Response:
    await db.users.update_tz_delta(user_id, tz_delta)
    return Response(status_code=status.HTTP_200_OK, content="User's time zone delta has been updated")


@router.get('/{user_id}/tz_delta')
async def get_time_zone_delta(
        user_id: schemas.TelegramUserId,
        db: DatabaseRepo = Depends(get_db)
) -> schemas.UserTimeZoneDeltaOut:
    tz_delta = await db.users.get_tz_delta(user_id) or 0
    return schemas.UserTimeZoneDeltaOut(tz_delta=tz_delta)


@router.get('/{user_id}/activities/summary')
async def get_activity_summary(
        user_id: schemas.TelegramUserId,
        db: DatabaseRepo = Depends(get_db)
) -> schemas.UserActivitiesSummaryOut:
    summary = await db.users.get_activities_summary(user_id)
    return schemas.UserActivitiesSummaryOut(
        data=[
            schemas.UserActivitySummary(type_id=activity_type, type_name=activity_type.name, amount=amount)
            for activity_type, amount in summary
        ]
    )
