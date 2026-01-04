import enum
from datetime import datetime, date, time, timedelta
from typing import List

from sqlalchemy import ForeignKey, String, TIMESTAMP, BIGINT, SMALLINT, UniqueConstraint, DATE
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import CheckConstraint, Index

from .func import db_utcnow


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)  # Telegram ID
    username: Mapped[str] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(10))
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=db_utcnow())
    last_activity: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=db_utcnow())
    notify_hours: Mapped[List[int]] = mapped_column(
        ARRAY(SMALLINT),
        nullable=False,
        default=list,
        server_default=text("'{}'::smallint[]"),
    )
    time_zone_delta: Mapped[int] = mapped_column(SMALLINT, default=0)  # In hours. UTC+3 => 3. UTC-2 => -2

    activities: Mapped[List["Activity"]] = relationship(back_populates="user", cascade="all")

    __table_args__ = (
        CheckConstraint(
            'time_zone_delta BETWEEN -12 AND 12',
            name='check_timezone_range'
        ),
        CheckConstraint(
            "array_length(notify_hours, 1) <= 24",
            name='check_notify_hours_max_length'
        ),
        CheckConstraint(
            "notify_hours <@ ARRAY[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]::smallint[]",
            name='check_notify_hours_range'
        ),
        Index('ix_users_notify_hours', notify_hours, postgresql_using='gin'),
    )

    def __repr__(self) -> str:
        return f"<User: {self.id} @{self.username}>"


class ActivityTypes(str, enum.Enum):
    SLEEP = "sleep"
    WORK = "work"
    STUDY = "study"
    FAMILY = "family"
    FRIENDS = "friends"
    RELAX = "relax"
    SPORT = "SPORT"
    GAMES = "games"


class Activity(Base):
    """ Class which represents user's activities (for an 1 hour) at a certain time """
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    utc_date: Mapped[date] = mapped_column(DATE, nullable=False)
    utc_hour: Mapped[int] = mapped_column(SMALLINT, nullable=False)  # 0-23

    user: Mapped["User"] = relationship(back_populates="activities")

    __table_args__ = (
        UniqueConstraint('user_id', 'utc_date', 'utc_hour', name='uix_user_id_time'),
        Index('ix_activity_date_hour', utc_date, utc_hour),
        Index('ix_activity_user_date', user_id, utc_date),
        CheckConstraint('utc_hour BETWEEN 0 AND 23', name='check_hour_range'),
    )

    @property
    def activity_type_enum(self) -> ActivityTypes:
        return ActivityTypes(self.type)

    @activity_type_enum.setter
    def activity_type_enum(self, value: ActivityTypes):
        self.type = value.value

    @property
    def start_datetime_utc(self) -> datetime:
        """ Start of activity in datetime (UTC) """
        return datetime.combine(self.utc_date, time(hour=self.utc_hour, minute=0))

    @property
    def end_datetime_utc(self) -> datetime:
        """ End of activity in datetime (after 1 hour)"""
        if self.utc_hour == 23:
            next_date = self.utc_date + timedelta(days=1)
            return datetime.combine(next_date, time(hour=0, minute=0))
        return datetime.combine(self.utc_date, time(self.utc_hour + 1, 0))

    def __repr__(self) -> str:
        return f'<Activity at {self.utc_date} {self.utc_hour}:00  type: {self.type}>'
