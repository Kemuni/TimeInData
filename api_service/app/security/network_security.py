import ipaddress
import json
from typing import Optional, List
from urllib.parse import unquote

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from loguru import logger
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from app.security.schemas import HTTPUserCredentials


class HTTPInternalNetworkAuth(SecurityBase):
    """ HTTP Authorization via IP address which should be in the trusted networks array """

    def __init__(  # noqa: Write own class like in the official FastAPI way
        self,
        *,
        trusted_networks: List[str],
        scheme_name: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error
        self.trusted_networks = trusted_networks

    async def __call__(self, request: Request) -> bool:
        client_ip = self._get_request_ip(request)
        if not self._is_from_trusted_network(client_ip):
            if self.auto_error:
                raise self.make_not_allowed_resource_error()
            else:
                return False

        return True

    @staticmethod
    def make_authenticate_headers() -> dict[str, str]:
        return {"WWW-Authenticate": "INTERNAL"}

    def make_not_authenticated_error(self) -> HTTPException:
        return HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers=self.make_authenticate_headers(),
        )

    def make_not_allowed_resource_error(self) -> HTTPException:
        """ Returns HTTP 403 Forbidden exception """
        return HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Not allowed to access this resource",
            headers=self.make_authenticate_headers(),
        )

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
        trusted_ip_networks = (ipaddress.ip_network(network) for network in self.trusted_networks)

        client_ip_address = ipaddress.ip_address(client_ip)
        return any(client_ip_address in network for network in trusted_ip_networks)


class HTTPInternalNetworkUserAuth(HTTPInternalNetworkAuth):
    """ HTTP Authorization via headers and IP address which should be in the trusted networks array """

    def __init__(
        self,
        *,
        trusted_networks: List[str],
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        super().__init__(
            trusted_networks=trusted_networks,
            scheme_name=scheme_name,
            auto_error=auto_error
        )
        description = (
            description
            or
            "Write user data from Telegram in the Authorization header.\n\n"
            "Format: \"INTERNAL <json_of_user_data>\"\n\n"
            "Example: \"INTERNAL {\"id\": 123456789, \"language_code\": \"en\", \"username\": \"user_name\"}\""
        )
        self.model = HTTPBearerModel(description=description)

    async def __call__(self, request: Request) -> Optional[HTTPUserCredentials]:
        is_allowed = await super().__call__(request)
        if not is_allowed:
            if self.auto_error:
                raise self.make_not_allowed_resource_error()
            else:
                return None

        authorization = request.headers.get("Authorization")

        scheme, raw_user_data = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and raw_user_data):
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None

        if scheme.lower() != "internal":
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None

        http_credentials = self._get_credentials_from_raw_user_data(raw_user_data)
        if not http_credentials:
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None
        return http_credentials

    @staticmethod
    def _get_credentials_from_raw_user_data(raw_user_data: str) -> Optional[HTTPUserCredentials]:
        """ Get user credentials from raw user data """
        try:
            user_data = json.loads(unquote(raw_user_data))
            return HTTPUserCredentials(
                user_id=user_data['id'],
                language_code=user_data['language_code'],
                username=user_data['username']
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid format of user data in headers. Error: {e}.")
            return None
