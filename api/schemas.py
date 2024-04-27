from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from api.database.models import ActivityTypes


def hour_validate(hour: int):
    assert 0 <= hour <= 23
    return hour


HourNumber = Annotated[int, AfterValidator(hour_validate)]


class UserBase(BaseModel):
    id: int
    username: str
    language: str


class User(UserBase):
    joined_at: datetime
    last_activity: datetime
    notify_hours: HourNumber


class UserNotifyHoursOut(BaseModel):
    notify_hours: List[HourNumber]


class ActivityBase(BaseModel):
    type: ActivityTypes
    time: datetime


class LastActivityOut(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
