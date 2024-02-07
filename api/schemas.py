from datetime import datetime
from typing import List

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    language: str
    joined_at: datetime
    last_activity: datetime
    notify_hours: List[int]
