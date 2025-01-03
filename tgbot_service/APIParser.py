import enum
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional

import httpx
from pydantic import Field
from pydantic.dataclasses import dataclass

from config import get_config


class ActivityTypes(enum.Enum):
    SLEEP = 1
    WORK = 2
    STUDYING = 3
    FAMILY = 4
    FRIENDS = 5
    PASSIVE = 6  # Something to relax
    EXERCISE = 7  # Physical exercises
    READING = 8


@dataclass
class ActivityBaseIn:
    type: int
    time: str = Field(..., title='Activity time in "%Y-%m-%dT%H:%M:%S" format')


@dataclass
class ActivityBaseOut:
    type: str
    time: str


@dataclass
class Activity(ActivityBaseOut):
    id: int


@dataclass
class ActivitySummary:
    type_name: str
    type_id: ActivityTypes
    amount: int


@dataclass
class ActivitiesSummaryOut:
    data: List[ActivitySummary]


@dataclass
class UserOut:
    id: int
    username: str
    language: str
    notify_hours: Optional[List[int]]
    tz_delta: int


class APIParser:
    """ Class for interaction with our API service. """

    API_DOMAIN: str = get_config().api_domain
    GET_HEALTHCHECK_URI: str = API_DOMAIN + "/healthcheck"
    PUT_USER_URI: str = API_DOMAIN + "/users"
    GET_USERS_TO_NOTIFY_URI: str = API_DOMAIN + "/users/to_notify"
    PUT_USER_NOTIFY_HOURS_URI: str = API_DOMAIN + "/users/{user_id}/notify_hours"
    PUT_USER_TZ_DELTA_URI: str = API_DOMAIN + "/users/{user_id}/tz_delta"
    GET_USER_NOTIFY_HOURS_URI: str = API_DOMAIN + "/users/{user_id}/notify_hours"
    GET_USER_TZ_DELTA_URI: str = API_DOMAIN + "/users/{user_id}/tz_delta"
    GET_USER_LAST_ACTIVITY_URI: str = API_DOMAIN + "/users/{user_id}/activities/last"
    POST_USER_ACTIVITIES_URI: str = API_DOMAIN + "/users/{user_id}/activities"
    GET_USER_ACTIVITIES_SUMMARY_URI: str = API_DOMAIN + "/users/{user_id}/activities/summary"

    DATETIME_FORMAT: str = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @staticmethod
    @asynccontextmanager
    async def create_client() -> AsyncIterator[httpx.AsyncClient]:
        """ Create and return httpx.AsyncClient for initializing APIParser class. """
        client = httpx.AsyncClient()
        try:
            yield client
        finally:
            await client.aclose()

    async def healthcheck(self) -> bool:
        """ Check API service is working. """
        response = await self.client.get(self.GET_HEALTHCHECK_URI, follow_redirects=True)
        return response.status_code == 200

    async def get_users_to_notify(self) -> List[int]:
        """
        Get list of users, that's need to notify in current UTC hour.
        :return: List of user_id which have to be notified.
        """
        response = await self.client.get(self.GET_USERS_TO_NOTIFY_URI)
        response.raise_for_status()
        data = response.json()
        return data["user_ids"]


    async def create_or_update_user(self, user_id: int, username: str, language: str) -> bool:
        """
        Create user or update user's data. Return bool is_new_user.

        :param user_id: Telegram ID of user.
        :param username: Telegram user's username.
        :param language: Telegram user's language.
        :return: True if it is new user, false otherwise.
        """
        user_data = {
            "id": user_id,
            "username": username,
            "language": language,
        }
        response = await self.client.put(self.PUT_USER_URI, json=user_data)
        response.raise_for_status()
        api_user = UserOut(**response.json())

        return response.status_code == 201 or api_user.notify_hours is None

    async def update_user_notify_hours(self, user_id: int, notify_hours: List[int]) -> None:
        """
        Update user notify hours.

        :param user_id: Telegram ID of user.
        :param notify_hours: Hours to notify user.
        """
        user_data = {
            "notify_hours": notify_hours
        }
        response = await self.client.put(self.PUT_USER_NOTIFY_HOURS_URI.format(user_id=user_id), json=user_data)
        response.raise_for_status()

    async def update_user_time_zone_delta(self, user_id: int, new_tz_delta: int) -> None:
        """
        Update user time zone delta.

        :param user_id: Telegram ID of user.
        :param new_tz_delta: New timezone delta.
        """
        user_data = {
            "tz_delta": new_tz_delta
        }
        response = await self.client.put(self.PUT_USER_TZ_DELTA_URI.format(user_id=user_id), json=user_data)
        response.raise_for_status()

    async def get_user_notify_hours(self, user_id: int) -> List[int]:
        """
        Get user hours for notifications.

        :param user_id: Telegram ID of user.
        :return: List of hours.
        """
        response = await self.client.get(self.GET_USER_NOTIFY_HOURS_URI.format(user_id=user_id))
        response.raise_for_status()
        data = response.json()
        return data["notify_hours"]

    async def get_user_time_zone_delta(self, user_id: int) -> int:
        """
        Get hours delta of time zone of user. For example, if user from Moscow, means UTC+3, method will return 3.

        :param user_id: Telegram ID of user.
        :return: Hours delta of time zone.
        """
        response = await self.client.get(self.GET_USER_TZ_DELTA_URI.format(user_id=user_id))
        response.raise_for_status()
        data = response.json()
        return data["tz_delta"]

    async def get_user_last_activity(self, user_id: int) -> Optional[Activity]:
        """
        Get the last activity of user with given user_id.

        :param user_id: Telegram ID of user.
        :return: If there is an activity return Activity dataclass, otherwise - None.
        """
        response = await self.client.get(self.GET_USER_LAST_ACTIVITY_URI.format(user_id=user_id))
        response.raise_for_status()
        data = response.json()
        return Activity(**data) if data else None

    async def add_user_activities(self, user_id: int, activities: List[ActivityBaseIn]) -> None:
        """
        Add user activities to user with given user_id.

        :param user_id: Telegram ID of user.
        :param activities: Activities to add.
        """
        activity_data = {
            "activities": [activity.__dict__ for activity in activities]
        }
        response = await self.client.post(self.POST_USER_ACTIVITIES_URI.format(user_id=user_id), json=activity_data)
        response.raise_for_status()

    async def get_activities_summary(self, user_id: int) -> Optional[ActivitiesSummaryOut]:
        """
        Get information about amount of user's activities.

        :param user_id: Telegram ID of user.
        :return: Activities summary info.
        """
        response = await self.client.get(self.GET_USER_ACTIVITIES_SUMMARY_URI.format(user_id=user_id))
        response.raise_for_status()
        data = response.json()
        return ActivitiesSummaryOut(**data) if data else None
