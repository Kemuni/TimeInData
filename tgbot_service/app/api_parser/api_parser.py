from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional, TypeVar, Type

import httpx
from pydantic import TypeAdapter, ValidationError

from app.api_parser.types import (
    APIResponse,
    UserOut,
    Activity,
    ActivityBaseIn,
    ActivitiesSummaryOut,
    UserNotificationsSettingsOut,
    UserTimeZoneDeltaOut
)
from app.config import get_config
from app.exceptions import APIError


T = TypeVar('T')
class APIParser:
    """ Class for interaction with our API service. """

    API_DOMAIN: str = get_config().api_domain
    GET_HEALTHCHECK_URI: str = API_DOMAIN + "/healthcheck"
    PUT_USER_URI: str = API_DOMAIN + "/users"
    PUT_USER_NOTIFICATIONS_SETTINGS_URI: str = API_DOMAIN + "/users/{user_id}/settings/notifications"
    GET_USER_NOTIFICATIONS_SETTINGS_URI: str = API_DOMAIN + "/users/{user_id}/settings/notifications"
    PUT_USER_TIMEZONE_SETTINGS_URI: str = API_DOMAIN + "/users/{user_id}/settings/timezone"
    GET_USER_TIMEZONE_SETTINGS_URI: str = API_DOMAIN + "/users/{user_id}/settings/timezone"
    GET_USER_LATEST_ACTIVITY_URI: str = API_DOMAIN + "/users/{user_id}/activities/latest"
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

    @staticmethod
    def _parse_response(response: httpx.Response, data_type: Type[T]) -> T:
        response.raise_for_status()

        adapter = TypeAdapter(APIResponse[data_type])   # type: ignore[valid-type]
        try:
            result: APIResponse[T] = adapter.validate_python(response.json())
        except ValidationError as e:
            raise APIError(
                code="INVALID_RESPONSE_DATA",
                message=str(e),
            )

        if not result.success or result.error:
            raise APIError(
                code=result.error.code if result.error else "UNKNOWN_ERROR",
                message=result.error.message if result.error else "UNKNOWN_ERROR",
            )


        return result.data

    async def healthcheck(self) -> bool:
        """ Check API service is working. """
        response = await self.client.get(self.GET_HEALTHCHECK_URI, follow_redirects=True)
        result = response.json()
        return result['success'] == True and response.status_code == 200

    async def create_or_update_user(self, user_id: int, username: str, language: str) -> bool:
        """
        Create user or update user's data. Return bool is_new_user.

        :param user_id: Telegram ID of user.
        :param username: Telegram user's username.
        :param language: Telegram user's language.
        :return: True if it is a new user, false otherwise.
        """
        user_data = {
            "id": user_id,
            "username": username,
            "language": language,
        }
        response = await self.client.put(self.PUT_USER_URI, json=user_data)
        user = self._parse_response(response, UserOut)

        return response.status_code == 201 or len(user.notify_hours) == 0

    async def update_user_notify_hours(self, user_id: int, notify_hours: List[int]) -> None:
        """
        Update users notify hours.

        :param user_id: Telegram ID of user.
        :param notify_hours: Hours to notify user.
        """
        user_data = {
            "notify_hours": notify_hours
        }
        response = await self.client.put(self.PUT_USER_NOTIFICATIONS_SETTINGS_URI.format(user_id=user_id), json=user_data)
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
        response = await self.client.put(self.PUT_USER_TIMEZONE_SETTINGS_URI.format(user_id=user_id), json=user_data)
        response.raise_for_status()

    async def get_user_notify_hours(self, user_id: int) -> List[int]:
        """
        Get user hours for notifications.

        :param user_id: Telegram ID of user.
        :return: List of hours.
        """
        response = await self.client.get(self.GET_USER_NOTIFICATIONS_SETTINGS_URI.format(user_id=user_id))
        notifications_settings = self._parse_response(response, UserNotificationsSettingsOut)
        return notifications_settings.notify_hours

    async def get_user_time_zone_delta(self, user_id: int) -> int:
        """
        Get hour's delta of user time zone. For example, if user from Moscow, means UTC+3, method will return 3.

        :param user_id: Telegram ID of user.
        :return: Hours delta of time zone.
        """
        response = await self.client.get(self.GET_USER_TIMEZONE_SETTINGS_URI.format(user_id=user_id))
        timezone_settings = self._parse_response(response, UserTimeZoneDeltaOut)
        return timezone_settings.tz_delta

    async def get_user_last_activity(self, user_id: int) -> Optional[Activity]:
        """
        Get the last activity of user with given user_id.

        :param user_id: Telegram ID of user.
        :return: If there is an activity return Activity dataclass, otherwise - None.
        """
        response = await self.client.get(self.GET_USER_LATEST_ACTIVITY_URI.format(user_id=user_id))
        activity = self._parse_response(response, Optional[Activity])
        return activity

    async def add_user_activities(self, user_id: int, activities: List[ActivityBaseIn]) -> None:
        """
        Add user activities to user with given user_id.

        :param user_id: Telegram ID of user.
        :param activities: Activities to add.
        """
        activity_data = {
            "activities": [TypeAdapter(ActivityBaseIn).dump_json(activity) for activity in activities]
        }
        response = await self.client.post(self.POST_USER_ACTIVITIES_URI.format(user_id=user_id), json=activity_data)
        response.raise_for_status()

    async def get_activities_summary(self, user_id: int) -> Optional[ActivitiesSummaryOut]:
        """
        Get information about the amount of user's activity.

        :param user_id: Telegram ID of user.
        :return: Activities summary info.
        """
        response = await self.client.get(self.GET_USER_ACTIVITIES_SUMMARY_URI.format(user_id=user_id))
        summary = self._parse_response(response, Optional[ActivitiesSummaryOut])
        return summary
