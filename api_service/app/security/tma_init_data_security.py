import hashlib
import hmac
import json
from datetime import datetime, UTC, timedelta
from typing import Optional
from urllib.parse import parse_qs, unquote

from fastapi import Request
from fastapi.security.http import HTTPBase
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from loguru import logger

from app.security.schemas import HTTPTMACredentials


class HTTPTMAInitDataAuth(HTTPBase):
    """ HTTP Authorization via Telegram Mini App (TMA) Init Data """

    TMA_INIT_DATA_EXPIRATION_IN_MINUTES: int = 2 * 60  # Auth date expiration time in minutes


    def __init__(  # noqa: Write own class like in the official FastAPI way
        self,
        *,
        tg_bot_token: str,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        description = (
            description
            or
            "Write your init data from Telegram Mini App in the Authorization header.\n\nFormat: \"TMA <init_data>\""
        )
        self.model = HTTPBearerModel(description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error
        self.tg_bot_token = tg_bot_token


    async def __call__(self, request: Request) -> Optional[HTTPTMACredentials]:
        authorization = request.headers.get("Authorization")

        scheme, raw_tma_init_data = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and raw_tma_init_data):
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None

        if scheme.lower() != "tma":
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None

        raw_tma_data = self._parse_raw_tma_init_data(raw_tma_init_data)
        if not raw_tma_data or not self._verify_tma_init_data(raw_tma_data):
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None

        http_tma_credentials = self._get_tma_credentials_from_init_data(raw_tma_data)
        if not http_tma_credentials:
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None

        return http_tma_credentials

    def make_authenticate_headers(self) -> dict[str, str]:
        return {"WWW-Authenticate": "TMA"}

    @staticmethod
    def _parse_raw_tma_init_data(raw_tma_init_data: str) -> dict[str, str]:
        """ Parse raw TMA init data to dict with key-value pairs """
        init_data = parse_qs(unquote(raw_tma_init_data))
        return {key: value[0] for key, value in init_data.items()}

    def _verify_tma_init_data(self, parsed_tma_init_data: dict[str, str]) -> bool:
        """ Verifying TMA init data by checking if it has valid hash and is not expired """
        try:
            auth_date_timestamp = int(parsed_tma_init_data.get('auth_date', '0'))
            logger.info(f"AUTH DATE TIMESTAMP: {auth_date_timestamp}")
            logger.info(f"is valid: {self._is_tma_init_data_valid(parsed_tma_init_data)}")
            logger.info(f"is expired: {self._is_date_expired(auth_date=datetime.fromtimestamp(auth_date_timestamp, UTC))}")
            return (
                    self._is_tma_init_data_valid(parsed_tma_init_data)
                    and not self._is_date_expired(auth_date=datetime.fromtimestamp(auth_date_timestamp, UTC))
            )
        except ValueError as e:
            logger.error(f"Invalid format of TMA init data. Error: {e}")
            return False

    def _is_tma_init_data_valid(self, parsed_tma_init_data: dict[str, str]) -> bool:
        """
        Check if TMA init data is valid by comparing hash with calculated hash
        Docs: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
        """
        init_hash = parsed_tma_init_data['hash'].strip()
        check_string_list = [f'{key}={value}' for key, value in parsed_tma_init_data.items() if key != 'hash']
        check_string = '\n'.join(sorted(check_string_list))

        secret_key = hmac.digest("WebAppData".encode("utf-8"), self.tg_bot_token.encode('utf-8'), hashlib.sha256)  # noqa
        our_hash = hmac.new(secret_key, check_string.encode('utf-8'), hashlib.sha256).hexdigest()  # noqa

        return hmac.compare_digest(our_hash, init_hash)

    def _is_date_expired(self, auth_date: datetime) -> bool:
        """
        Check if auth date is expired.
        Auth_date + `TMA_INIT_DATA_EXPIRATION_IN_MINUTES` should be less than current UTC time
        """
        return auth_date + timedelta(minutes=self.TMA_INIT_DATA_EXPIRATION_IN_MINUTES) < datetime.now(UTC)

    @staticmethod
    def _get_tma_credentials_from_init_data(parsed_init_data: dict[str, str]) -> Optional[HTTPTMACredentials]:
        """ Get TMA credentials from parsed init data """
        try:
            user_data = json.loads(unquote(parsed_init_data['user']))
            return HTTPTMACredentials(
                user_id=user_data['id'],
                language_code=user_data['language_code'],
                username=user_data['username']
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid format of TMA init data. Error: {e}")
            return None
