from datetime import date, datetime
from typing import List, TypeVar, Any, Generic, Optional

from pydantic.dataclasses import dataclass

from app.types.activity_types import ActivityTypes


@dataclass(slots=True)
class ActivityBaseIn:
    type: str
    utc_hour: int
    utc_date: date


@dataclass(slots=True)
class ActivityBaseOut:
    type: str
    utc_hour: int
    utc_date: date


@dataclass(slots=True)
class Activity(ActivityBaseOut):
    id: int


@dataclass(slots=True)
class ActivitySummary:
    activity_type: ActivityTypes
    hours_amount: int


@dataclass(slots=True)
class ActivitiesSummaryOut:
    summary: List[ActivitySummary]


@dataclass(slots=True)
class UserOut:
    id: int
    username: str
    language: str
    notify_utc_hours: List[int]
    tz_delta: int
    created_at: datetime
    last_interaction_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class UserNotificationsSettingsOut:
    notify_utc_hours: List[int]
    notify_local_hours: List[int]


@dataclass(slots=True)
class UserTimeZoneDeltaOut:
    tz_delta: int


@dataclass(slots=True)
class DateRange:
    from_date: datetime
    to_date: datetime


@dataclass(slots=True)
class MissingActivitySlot:
    utc_date: date
    utc_hour: int


@dataclass(slots=True)
class MissingActivitySlotsData:
    has_missing_slots: bool
    date_range: Optional[DateRange]
    missing_slots: Optional[List[MissingActivitySlot]]


@dataclass(slots=True)
class APIErrorDetail:
    code: str
    message: str



ApiData = TypeVar('ApiData', bound=Any)
@dataclass(slots=True)
class APIResponse(Generic[ApiData]):
    success: bool
    data: Optional[ApiData]
    error: Optional[APIErrorDetail]


@dataclass(slots=True, frozen=True)
class UserNotifyHours:
    utc_hours: List[int]
    local_hours: List[int]
