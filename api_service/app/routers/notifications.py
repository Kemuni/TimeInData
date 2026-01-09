from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app import schemas
from app.database.repositories import DatabaseRepo
from app.dependencies import get_db
from app.utils.response import SuccessResponse
from app.utils.utcnow import utcnow

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get(
    '/set_activities_reminder/pending',
    response_model=schemas.APIResponse[schemas.PendingNotificationsOut],
)
async def get_set_activities_pending(db: DatabaseRepo = Depends(get_db)):
    """ Get users, which a needed to be notified (set activities) in the current UTC hour. """
    user_ids = await db.users.get_ids_to_notify(utcnow().hour) or []
    data = schemas.PendingNotificationsOut(
        type='set_activities_reminder',
        user_ids=user_ids,
        total_notifications=len(user_ids),
    ).model_dump()
    return SuccessResponse(data=data)