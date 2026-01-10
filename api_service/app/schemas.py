from datetime import datetime, date, time
from typing import List, Literal, Any, Generic, TypeVar

from annotated_types import Gt, Ge, Le
from pydantic import BaseModel, ConfigDict, field_serializer, Field, field_validator
from pydantic_core._pydantic_core import PydanticCustomError
from typing_extensions import Annotated, Optional

from app.database.models import ActivityTypes

T = TypeVar('T')


TelegramUserId = Annotated[int, Gt(0)]
HourNumber = Annotated[int, Ge(0), Le(23)]
TzDeltaNumber = Annotated[int, Ge(-12), Le(12)]


class ErrorDetail(BaseModel):
    """Standard error detail format"""
    code: str
    message: str


class APIResponse(BaseModel, Generic[T]):
    """Standard API response format"""
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None


class MessageResponse(BaseModel):
    message: str


class UserBase(BaseModel):
    id: int = Field(..., serialization_alias="user_id")
    username: str
    language: str


class UserNotificationsSettingsOut(BaseModel):
    notify_utc_hours: List[HourNumber]
    notify_local_hours: List[HourNumber]


class UserNotificationsSettingsIn(BaseModel):
    notify_hours: List[HourNumber] = Field(..., max_length=24)

    @field_validator("notify_hours", mode="after")
    def validate_notify_hours(cls, v: List[int]) -> List[int]:
        if len(v) != len(set(v)):
            raise PydanticCustomError(
                'notify_hours_duplicate',
                "Notify hours in the list must be unique.",
            )
        return sorted(v)


class UserTimeZoneDeltaOut(BaseModel):
    tz_delta: TzDeltaNumber


class UserOut(UserBase):
    id: int
    notify_utc_hours: List[HourNumber]
    time_zone_delta: TzDeltaNumber = Field(..., serialization_alias="tz_delta")
    last_interaction_at: datetime
    created_at: datetime
    updated_at: datetime


class UserActivitySummary(BaseModel):
    activity_type: str
    hours_amount: int


class UserActivitiesSummaryOut(BaseModel):
    data: List[UserActivitySummary]

class PendingNotificationsOut(BaseModel):
    type: Literal['set_activities_reminder']
    user_ids: List[int]
    total_notifications: int


class ActivityBase(BaseModel):
    type: ActivityTypes
    utc_date: date
    utc_hour: int


class ActivityIn(ActivityBase):
    @field_serializer("type")
    def serialize_type(self, type_: ActivityTypes):
        return type_.name

    def timestamp(self) -> float:
        return datetime.combine(self.utc_date, time(hour=self.utc_hour, minute=0)).timestamp()


class ActivityOut(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class MissingActivitySlot(BaseModel):
    utc_date: date
    utc_hour: int


class DateRange(BaseModel):
    from_date: datetime
    to_date: datetime


class MissingActivitySlotsOut(BaseModel):
    has_missing_slots: bool
    date_range: Optional[DateRange] = None
    missing_slots: Optional[List[MissingActivitySlot]] = None
    total_missing: int
