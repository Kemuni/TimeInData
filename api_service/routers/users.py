from datetime import datetime
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, status, Body, HTTPException

from api_service import schemas
from api_service.database.repositories import DatabaseRepo
from api_service.dependencies import get_db

router = APIRouter(prefix='/users', tags=['users'])


@router.put('', status_code=status.HTTP_200_OK)
async def create_or_update(user: schemas.UserBase, db: DatabaseRepo = Depends(get_db)):
    await db.users.create_or_update(**user.model_dump())


@router.put('/{user_id}/notify_hours', status_code=status.HTTP_200_OK)
async def update_notify_hours(
        user_id: int,
        notify_hours: Annotated[List[schemas.HourNumber], Body(embed=True)],
        db: DatabaseRepo = Depends(get_db)
):
    await db.users.update_notify_hours(user_id, notify_hours)


@router.get('/{user_id}/notify_hours')
async def get_notify_hours(user_id: int, db: DatabaseRepo = Depends(get_db)) -> schemas.UserNotifyHoursOut:
    notify_hours = await db.users.get_notify_hours(user_id) or []
    return schemas.UserNotifyHoursOut(notify_hours=notify_hours)


@router.get('/{user_id}/activities/last', response_model_exclude={'user_id'})
async def get_last_activity(user_id: int, db: DatabaseRepo = Depends(get_db)) -> Optional[schemas.LastActivityOut]:
    last_activity = await db.users.get_last_activity(user_id)
    return schemas.LastActivityOut.model_validate(last_activity) if last_activity else None


@router.post('/{user_id}/activities', status_code=status.HTTP_201_CREATED)
async def add_activities(
        user_id: int,
        activities: Annotated[List[schemas.ActivityBase], Body(embed=True)],
        db: DatabaseRepo = Depends(get_db)
):
    for activity in activities:
        if activity.time > datetime.now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Incorrect activity time. {activity.time} is invalid")
    await db.users.add_activities(user_id, activities)
