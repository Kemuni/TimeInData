import enum
from datetime import date, datetime
from typing import List, TypeVar, Any, Generic, Optional

from pydantic.dataclasses import dataclass
from pydantic import Field


class ActivityTypes(str, enum.Enum):
    SLEEP = "SLEEP"
    WORK = "WORK"
    STUDY = "STUDY"
    FAMILY = "FAMILY"
    FRIENDS = "FRIENDS"
    RELAX = "RELAX"
    SPORT = "SPORT"
    GAMES = "GAMES"


@dataclass(slots=True)
class ActivityBaseIn:
    type: int
    utc_hour: int
    utc_date: date = Field(..., title='Activity date in "%Y-%m-%d" format')


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
    type_name: str
    type_id: ActivityTypes
    amount: int


@dataclass(slots=True)
class ActivitiesSummaryOut:
    data: List[ActivitySummary]


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
