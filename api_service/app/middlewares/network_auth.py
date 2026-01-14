import hashlib
import hmac
import ipaddress
import json
from datetime import datetime, UTC, timedelta
from http import HTTPStatus
from typing import Any, Optional
from urllib.parse import parse_qs, unquote

from fastapi import Request, HTTPException
from loguru import logger
from pydantic import BaseModel, dataclasses
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class NetworkOrTMAAuthMiddleware(BaseHTTPMiddleware):
    """ Middleware for checking if request is from trusted network or has valid TMA init data with fresh `auth_date` """
    USER_DATA_HEADER_KEY: str = 'User-Data'
    TMA_INIT_DATA_HEADER_KEY: str = 'TMA-Init-Data'
    TMA_INIT_DATA_EXPIRATION_MINUTES: int = 6 * 60  # Auth date expiration time in minutes

    def __init__(self, app, allowed_networks: list[str], tg_bot_token: str):
        super().__init__(app)
        self.allowed_networks = allowed_networks
        self.tg_bot_token = tg_bot_token

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_ip = self._get_request_ip(request)
        logger.info(f"Got request from IP: {request_ip}")
        if self._is_from_trusted_network(request_ip):
            user_data = self._get_user_data_from_headers(request)
            logger.info(f"Trusted user_data is: {user_data}")
        else:
            logger.info(f"{request_ip} is not trusted")
            raw_tma_data = self._get_raw_tma_init_data(request)
            if not raw_tma_data or not self._verify_tma_init_data(raw_tma_data):
                raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Access denied: Unauthorized")
            user_data = self._get_user_data_from_init_data(raw_tma_data)
            logger.info(f"Untrusted user_data is: {user_data}")

        if not user_data:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Access denied: Unauthorized")

        request.state.user_id = user_data.user_id
        request.state.user_language = user_data.language
        request.state.user_username = user_data.username

        return await call_next(request)

    def _verify_tma_init_data(self, raw_tma_data: dict[str, str]) -> bool:
        try:
            auth_date_timestamp = int(raw_tma_data.get('auth_date', '0'))
            return (
                self._is_tma_init_data_valid(raw_tma_data)
                and self._check_date_expiry(auth_date=datetime.fromtimestamp(auth_date_timestamp, UTC))
            )
        except ValueError as e:
            logger.error(f"Invalid format of init data. Error: {e}")
            return False

    def _check_date_expiry(self, auth_date: datetime):
        return auth_date + timedelta(minutes=self.TMA_INIT_DATA_EXPIRATION_MINUTES) > datetime.now(UTC)

    def _get_raw_tma_init_data(self, request: Request) -> Optional[dict[str, str]]:
        if self.TMA_INIT_DATA_HEADER_KEY in request.headers:
            init_data = parse_qs(unquote(request.headers[self.TMA_INIT_DATA_HEADER_KEY]))
            return {key: value[0] for key, value in init_data.items()}
        return None

    @staticmethod
    def _get_user_data_from_init_data(raw_init_data: dict[str, Any]) -> Optional['UserData']:
        try:
            user_data = json.loads(unquote(raw_init_data['user']))
            return UserData(
                user_id=user_data['id'],
                language=user_data['language_code'],
                username=user_data['username']
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid format of init data. Error: {e}")
            return None

    def _get_user_data_from_headers(self, request: Request) -> Optional['UserData']:
        if self.USER_DATA_HEADER_KEY in request.headers:
            try:
                user_data = json.loads(request.headers[self.USER_DATA_HEADER_KEY])
                return UserData(
                    user_id=user_data['id'],
                    language=user_data['language_code'],
                    username=user_data['username']
                )
            except (KeyError, ValueError) as e:
                logger.error(f"Invalid format of user data in headers. Error: {e}.")
                return None
        return None

    def _is_tma_init_data_valid(self, raw_init_data: dict[str, Any]) -> bool:
        init_hash = raw_init_data['hash'][0]
        check_string_list = [f'{key}={value[0]}' for key, value in raw_init_data.items() if key != 'hash']
        check_string = '\n'.join(sorted(check_string_list))

        secret_key = hmac.digest("WebAppData".encode("utf-8"), self.tg_bot_token.encode('utf-8'), hashlib.sha256)
        client_hash = hmac.new(secret_key, check_string.encode('utf-8'), hashlib.sha256).hexdigest()

        return hmac.compare_digest(client_hash, init_hash)

    @staticmethod
    def _get_request_ip(request: Request) -> str:
        """ Get client ip address from request """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "127.0.0.1"

    def _is_from_trusted_network(self, client_ip: str) -> bool:
        """ Check if request is from config trusted network (mostly Docker network) """
        allowed_networks = (ipaddress.ip_network(network) for network in self.allowed_networks)

        client_ip_address = ipaddress.ip_address(client_ip)
        return any(client_ip_address in network for network in allowed_networks)



class TMAData(BaseModel):
    user: dict[str, Any]
    chat_instance: str
    chat_type: str
    auth_date: int
    signature: str
    hash: str


@dataclasses.dataclass
class UserData:
    user_id: int
    language: str
    username: str
