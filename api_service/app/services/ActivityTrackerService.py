from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from app.database.repositories import DatabaseRepo
from app.utils.utcnow import utcnow


@dataclass(slots=True)
class MissingSlotsDateRange:
    from_date: datetime  # Start time (inclusive)
    to_date: datetime  # End time (inclusive)

    @property
    def total_hours(self) -> int:
        """ Total hours in the date range """
        return int((self.to_date - self.from_date).total_seconds() // 3600) + 1


class ActivityTrackerService:
    DEFAULT_MAX_CLOSEST_MISSING_SLOTS: int = 24
    MAX_CLOSETS_MISSING_SLOTS_FOR_NEWBIE: int = 6

    def __init__(self, db: DatabaseRepo, user_id: int):
        self.db = db
        self.user_id = user_id

    async def get_closest_missing_slots_date_range(
            self, max_missing_slots: int = DEFAULT_MAX_CLOSEST_MISSING_SLOTS
    ) -> Optional[MissingSlotsDateRange]:
        """
        Get the closest missing slots to set activities for user with `user_id`. For newbie users, we display fewer
        slots.
        :param max_missing_slots: The maximum missing slots (hours) to return.
        :return: MissingSlotsDateRange or None if there are no missing slots.
        """
        last_activity = await self.db.users.get_latest_activity(self.user_id)
        utc_now = utcnow()
        is_new_user = last_activity is None

        if is_new_user:
            max_missing_slots = min(self.MAX_CLOSETS_MISSING_SLOTS_FOR_NEWBIE, max_missing_slots)
            from_date = (
                datetime(utc_now.year, utc_now.month, utc_now.day, utc_now.hour) - timedelta(hours=max_missing_slots)
            )
        else:
            # If the last activity was too far from now, we return the closest missing slots
            from_date = max(
                last_activity.start_datetime_utc + timedelta(hours=1),
                datetime(utc_now.year, utc_now.month, utc_now.day, utc_now.hour) - timedelta(hours=max_missing_slots)
            )
            if (utc_now - from_date) <= timedelta(hours=1):
                return None

        to_date = min(
            from_date + timedelta(hours=max_missing_slots),
            # if now is 22:33, we can set activity only to 21:00, so we subtract 1 hour
            datetime(utc_now.year, utc_now.month, utc_now.day, utc_now.hour - 1)
        )
        return MissingSlotsDateRange(from_date=from_date, to_date=to_date)

