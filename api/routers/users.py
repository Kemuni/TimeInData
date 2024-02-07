from typing import List, Optional

from fastapi import APIRouter, Depends

from api import schemas
from api.dependencies import get_db
from database import DatabaseRepo

router = APIRouter(prefix='/users', tags=['users'])


@router.get(
    '',
    tags=['users'],
    response_model=List[schemas.User],
)
async def get_users(db: DatabaseRepo = Depends(get_db)):
    return await db.users.get_all()


@router.get(
    '/{user_id}',
    tags=['users'],
    response_model=Optional[schemas.User],
)
async def get_user_by_id(user_id: int, db: DatabaseRepo = Depends(get_db)):
    return await db.users.get_by_id(user_id=user_id)
