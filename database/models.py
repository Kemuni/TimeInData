import enum
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, String, TIMESTAMP, BIGINT, ARRAY, SMALLINT
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database import func


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BIGINT, unique=True)  # user telegram id
    username: Mapped[str] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(10))
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.utcnow())
    last_activity: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.utcnow())
    notify_hours: Mapped[List[int]] = mapped_column(ARRAY(SMALLINT), nullable=True)

    activities: Mapped[List["Activity"]] = relationship(back_populates="user", cascade="all")

    def __repr__(self) -> str:
        return f"<User: {self.user_id}>"


class ActivityType(enum.Enum):
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

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[ActivityType]
    time: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.utcnow())

    user: Mapped["User"] = relationship(back_populates="activities")

    def __repr__(self) -> str:
        return f'<Activity at {self.time.strftime("%d/%m/%Y at %H hours")} type: {self.type}>'
