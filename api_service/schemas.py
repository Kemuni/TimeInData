from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from api_service.database.models import ActivityTypes


def hour_validate(hour: int):
    assert 0 <= hour <= 23
    return hour


HourNumber = Annotated[int, AfterValidator(hour_validate)]


class UserBase(BaseModel):
    id: int
    username: str
    language: str


class UserNotifyHoursOut(BaseModel):
    notify_hours: List[HourNumber]


class ActivityBase(BaseModel):
    type: ActivityTypes
    time: datetime

    @field_serializer("type")
    def serialize_type(self, type: ActivityTypes):
        return type.name


class LastActivityOut(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
