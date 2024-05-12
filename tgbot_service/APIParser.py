import enum
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional

import httpx
from pydantic.dataclasses import dataclass

from tgbot_service.config import get_config


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
    time: str


@dataclass
class ActivityBaseOut:
    type: str
    time: str


@dataclass
class Activity(ActivityBaseOut):
    id: int


class APIParser:
    """ Class for interaction with our API service. """
    HTTPS_PREFIX: str = f"http{'' if get_config().debug else 's'}://{get_config().api.domain}:{get_config().api.port}/"
    PUT_USER_URI: str = HTTPS_PREFIX + "users"
    PUT_USER_NOTIFY_HOURS_URI: str = HTTPS_PREFIX + "users/{user_id}/notify_hours"
    GET_USER_NOTIFY_HOURS_URI: str = HTTPS_PREFIX + "users/{user_id}/notify_hours"
    GET_USER_LAST_ACTIVITY_URI: str = HTTPS_PREFIX + "users/{user_id}/activities/last"
    POST_USER_ACTIVITIES_URI: str = HTTPS_PREFIX + "users/{user_id}/activities"

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

    async def create_or_update_user(self, user_id: int, username: str, language: str) -> None:
        """
        Create user or update user's data.

        :param user_id: Telegram ID of user.
        :param username: Telegram user's username.
        :param language: Telegram user's language.
        """
        user_data = {
            "id": user_id,
            "username": username,
            "language": language,
        }
        response = await self.client.put(self.PUT_USER_URI, json=user_data)
        response.raise_for_status()

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
