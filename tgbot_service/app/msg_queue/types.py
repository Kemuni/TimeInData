import enum
from pydantic import BaseModel, Field


class ReminderMessageType(str, enum.Enum):
    SET_ACTIVITIES = "SET_ACTIVITIES"


class ReminderRabbitMessage(BaseModel):
    type: ReminderMessageType = Field(..., description="Type of reminder message for user")
    user_ids: list[int] = Field(..., description="List of user telegram IDs to notify")

