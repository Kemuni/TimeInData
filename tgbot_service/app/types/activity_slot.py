from dataclasses import dataclass
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

from app.types import ActivityTypes


class ActivitySlot(BaseModel):
    utc_hour: int
    utc_date: date
    local_hour: int
    local_date: date
    activity_type: Optional[ActivityTypes]


@dataclass(slots=True)
class ActivitySlotsFilterByLocalDate:
    local_date: date
    activity_slots: List[ActivitySlot]


ActivitySlotsStore = dict[int, ActivitySlot]
