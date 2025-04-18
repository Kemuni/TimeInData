import random
from datetime import datetime
from typing import Optional

import schemas
from database.models import ActivityTypes, Activity
from tests.utils.utils import get_random_number, get_random_datetime

ACTIVITY_TYPES_ARRAY = [i for i in ActivityTypes]


def get_random_activity_type() -> ActivityTypes:
    return random.choice(ACTIVITY_TYPES_ARRAY)


def get_random_activity_model(
        user_id: int,
        _id: Optional[int] = None,
        _type: Optional[ActivityTypes] = None,
        time: Optional[datetime] = None,
):
    """ Create random model of `Activity`. NO OBJECT CREATION IN DATABASE. """
    return Activity(
        id=_id or get_random_number(),
        user_id=user_id,
        type=_type or get_random_activity_type(),
        time=time or get_random_datetime(),
    )


def get_random_activity_base(
        _type: Optional[ActivityTypes] = None,
        time: Optional[datetime] = None,
) -> schemas.ActivityBase:
    """ Create random schema of `ActivityBase`. """
    return schemas.ActivityBase(
        type=_type or get_random_activity_type(),
        time=time or get_random_datetime(),
    )
