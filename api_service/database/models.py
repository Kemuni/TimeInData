import enum
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, String, TIMESTAMP, BIGINT, SMALLINT
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .func import utcnow


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)  # Telegram ID
    username: Mapped[str] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(10))
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=utcnow())
    last_activity: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=utcnow())
    notify_hours: Mapped[List[int]] = mapped_column(ARRAY(SMALLINT), nullable=True)
    time_zone_delta: Mapped[int] = mapped_column(SMALLINT, default=0)  # In hours. UTC+3 = 3. UTC-2 = -2

    activities: Mapped[List["Activity"]] = relationship(back_populates="user", cascade="all")

    def __repr__(self) -> str:
        return f"<User: {self.id}>"


class ActivityTypes(enum.Enum):
    SLEEP = 1
    WORK = 2
    STUDYING = 3
    FAMILY = 4
    FRIENDS = 5
    PASSIVE = 6  # Something to relax
    EXERCISE = 7  # Physical exercises
    READING = 8


class Activity(Base):
    """ Class which represents user's activities at a certain time """
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[ActivityTypes]
    time: Mapped[datetime] = mapped_column(TIMESTAMP, default=utcnow())

    user: Mapped["User"] = relationship(back_populates="activities")

    def __repr__(self) -> str:
        return f'<Activity at {self.time.strftime("%d/%m/%Y at %H hours")} type: {self.type}>'
