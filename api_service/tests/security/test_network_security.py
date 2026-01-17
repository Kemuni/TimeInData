import json
from urllib.parse import quote

import pytest
from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from app.security.network_security import HTTPInternalNetworkAuth, HTTPInternalNetworkUserAuth
from app.security.schemas import HTTPUserCredentials
from tests.utils.auth_headers import get_internal_auth_headers
from tests.utils.mock_request import create_mock_request


async def test_trusted_network_allows_access():
    trusted_networks = ["127.0.0.0/8", "10.0.0.0/8"]
    network_auth = HTTPInternalNetworkAuth(trusted_networks=trusted_networks, auto_error=False)

    mock_request = create_mock_request(ip_address="127.0.0.1")
    result = await network_auth(mock_request)
    
    assert result is True


async def test_untrusted_network_denies_access():
    trusted_networks = ["10.0.0.0/8"]
    network_auth = HTTPInternalNetworkAuth(trusted_networks=trusted_networks, auto_error=False)

    mock_request = create_mock_request(ip_address="192.168.1.100")
    result = await network_auth(mock_request)
    
    assert result is False


async def test_auto_error_raises_forbidden():
    trusted_networks = ["10.0.0.0/8"]
    network_auth = HTTPInternalNetworkAuth(trusted_networks=trusted_networks, auto_error=True)

    mock_request = create_mock_request(ip_address="192.168.1.100")
    
    with pytest.raises(HTTPException) as exc_info:
        await network_auth(mock_request)
    
    assert exc_info.value.status_code == HTTP_403_FORBIDDEN


async def test_x_forwarded_for_header():
    trusted_networks = ["10.0.0.0/8"]
    network_auth = HTTPInternalNetworkAuth(trusted_networks=trusted_networks, auto_error=False)

    mock_request = create_mock_request(
        ip_address="127.0.0.1",
        headers={"X-Forwarded-For": "10.0.0.5, 192.168.1.1"}
    )
    result = await network_auth(mock_request)
    
    assert result is True


async def test_x_real_ip_header():
    trusted_networks = ["10.0.0.0/8"]
    network_auth = HTTPInternalNetworkAuth(trusted_networks=trusted_networks, auto_error=False)
    
    mock_request = create_mock_request(
        ip_address="127.0.0.1",
        headers={"X-Real-IP": "10.0.0.10"}
    )
    result = await network_auth(mock_request)
    
    assert result is True


async def test_multiple_trusted_networks():
    trusted_networks = ["127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12"]
    network_auth = HTTPInternalNetworkAuth(trusted_networks=trusted_networks, auto_error=False)
    
    mock_request1 = create_mock_request(ip_address="127.0.0.1")
    assert await network_auth(mock_request1) is True
    
    mock_request2 = create_mock_request(ip_address="10.5.5.5")
    assert await network_auth(mock_request2) is True

    mock_request3 = create_mock_request(ip_address="172.16.0.1")
    assert await network_auth(mock_request3) is True

    mock_request4 = create_mock_request(ip_address="192.168.1.1")
    assert await network_auth(mock_request4) is False


def test_get_request_ip_priority():
    """Test that X-Forwarded-For has priority over X-Real-IP"""
    trusted_networks = ["127.0.0.0/8"]
    network_auth = HTTPInternalNetworkAuth(trusted_networks=trusted_networks)

    mock_request = create_mock_request(
        ip_address="10.0.0.1",
        headers={"X-Forwarded-For": "127.0.0.1", "X-Real-IP": "192.168.1.1"}
    )
    
    client_ip = network_auth._get_request_ip(mock_request)
    assert client_ip == "127.0.0.1"


def test_make_authenticate_headers():
    trusted_networks = ["127.0.0.0/8"]
    network_auth = HTTPInternalNetworkAuth(trusted_networks=trusted_networks)
    
    headers = network_auth.make_authenticate_headers()
    
    assert headers == {"WWW-Authenticate": "INTERNAL"}


async def test_network_user_auth_valid_credentials():
    trusted_networks = ["127.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks, auto_error=False)

    auth_header = get_internal_auth_headers(user_id=123456789, username="test_user", language_code="en")
    mock_request = create_mock_request(
        ip_address="127.0.0.1",
        headers=auth_header,
    )
    
    credentials = await user_auth(mock_request)
    
    assert credentials is not None
    assert isinstance(credentials, HTTPUserCredentials)
    assert credentials.user_id == 123456789
    assert credentials.username == "test_user"
    assert credentials.language_code == "en"


async def test_network_user_auth_untrusted_network():
    trusted_networks = ["10.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks, auto_error=False)
    
    auth_header = get_internal_auth_headers(user_id=123456789, username="test_user", language_code="en")
    mock_request = create_mock_request(
        ip_address="192.168.1.100",
        headers=auth_header,
    )
    
    credentials = await user_auth(mock_request)
    
    assert credentials is None


async def test_network_user_auth_missing_authorization():
    trusted_networks = ["127.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks, auto_error=False)

    mock_request = create_mock_request(ip_address="127.0.0.1")
    
    credentials = await user_auth(mock_request)
    
    assert credentials is None


async def test_network_user_auth_wrong_scheme():
    trusted_networks = ["127.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks, auto_error=False)

    user_data = json.dumps({"id": 123456789, "username": "test_user", "language_code": "en"})
    mock_request = create_mock_request(
        ip_address="127.0.0.1",
        auth_header=f"Bearer {user_data}",
    )
    
    credentials = await user_auth(mock_request)
    
    assert credentials is None


async def test_network_user_auth_malformed_json():
    trusted_networks = ["127.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks, auto_error=False)
    
    mock_request = create_mock_request(
        ip_address="127.0.0.1",
        auth_header="INTERNAL not_a_json",
    )
    
    credentials = await user_auth(mock_request)
    
    assert credentials is None


async def test_network_user_auth_incomplete_user_data():
    trusted_networks = ["127.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks, auto_error=False)
    
    incomplete_user_data = json.dumps({"id": 123456789})
    mock_request = create_mock_request(
        ip_address="127.0.0.1",
        auth_header=f"INTERNAL {incomplete_user_data}",
    )
    
    credentials = await user_auth(mock_request)
    
    assert credentials is None


async def test_network_user_auth_auto_error_untrusted():
    trusted_networks = ["10.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks, auto_error=True)

    auth_headers = get_internal_auth_headers(user_id=123456789, username="test_user", language_code="en")
    mock_request = create_mock_request(
        ip_address="192.168.1.100",
        headers=auth_headers,
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await user_auth(mock_request)
    
    assert exc_info.value.status_code == HTTP_403_FORBIDDEN


async def test_network_user_auth_auto_error_no_credentials():
    trusted_networks = ["127.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks, auto_error=True)
    
    mock_request = create_mock_request(ip_address="127.0.0.1")
    
    with pytest.raises(HTTPException) as exc_info:
        await user_auth(mock_request)
    
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED


def test_get_credentials_from_raw_user_data():
    """Test parsing user data from authorization header"""
    trusted_networks = ["127.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks)
    
    user_data = json.dumps({"id": 123456789, "username": "test_user", "language_code": "en"})
    credentials = user_auth._get_credentials_from_raw_user_data(user_data)
    
    assert credentials is not None
    assert credentials.user_id == 123456789
    assert credentials.username == "test_user"
    assert credentials.language_code == "en"


def test_get_credentials_from_url_encoded_data():
    """Test parsing URL-encoded user data"""
    trusted_networks = ["127.0.0.0/8"]
    user_auth = HTTPInternalNetworkUserAuth(trusted_networks=trusted_networks)
    
    user_data = json.dumps({"id": 123456789, "username": "test_user", "language_code": "en"})
    encoded_data = quote(user_data)
    credentials = user_auth._get_credentials_from_raw_user_data(encoded_data)
    
    assert credentials is not None
    assert credentials.user_id == 123456789
    assert credentials.username == "test_user"
    assert credentials.language_code == "en"
