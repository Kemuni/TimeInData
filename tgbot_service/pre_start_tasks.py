""" File with various tasks before starting this service """
import logging
from typing import Optional

from loguru import logger
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from tgbot_service.APIParser import APIParser


class UnableConnectToAPIError(Exception):
    """ Raised when our service unable to connect to API service  """

    def __init__(self, msg: Optional[str] = None):
        super().__init__(
            msg or """Unable to connect to API. Please check your internet connection and try again."""
        )


@retry(
    stop=stop_after_attempt(60 * 1),  # 60 attempts ~ 1 minute
    wait=wait_fixed(1),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def check_api_service_connection() -> None:
    """ Checking that we are able to connect to our API service. We try to do this for 5 minutes. """
    logger.info('Checking API service connection...')
    async with APIParser.create_client() as client:
        api = APIParser(client)
        if await api.healthcheck() is False:
            raise UnableConnectToAPIError()
        logger.info('Successfully connect to API service!')
