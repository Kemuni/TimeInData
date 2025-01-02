from datetime import datetime
from typing import List

from annotated_types import Gt, Lt
from pydantic import BaseModel, ConfigDict, field_serializer, Field
from typing_extensions import Annotated

from database.models import ActivityTypes

TelegramUserId = Annotated[int, Gt(0)]
HourNumber = Annotated[int, Gt(-1), Lt(24)]
TzDeltaNumber = Annotated[int, Gt(-13), Lt(13)]


class UserBase(BaseModel):
    id: int = Field(..., serialization_alias="user_id")
    username: str
    language: str


class UserNotifyHoursOut(BaseModel):
    notify_hours: List[HourNumber]


class UserTimeZoneDeltaOut(BaseModel):
    tz_delta: TzDeltaNumber


class UsersToNotifyOut(BaseModel):
    user_ids: List[int]


class ActivityBase(BaseModel):
    type: ActivityTypes
    time: datetime

    @field_serializer("type")
    def serialize_type(self, type: ActivityTypes):
        return type.name


class LastActivityOut(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
