import hashlib
import hmac
import json
from datetime import datetime, UTC, timedelta
from urllib.parse import quote

import pytest
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.security.schemas import HTTPTMACredentials
from app.security.tma_init_data_security import HTTPTMAInitDataAuth
from tests.utils.auth_headers import create_tma_init_data
from tests.utils.mock_request import create_mock_request


async def test_valid_tma_init_data():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token, auto_error=True)
    
    init_data = create_tma_init_data(bot_token, user_id=123456789, username="test_user", language_code="en")
    mock_request = create_mock_request(auth_header=f"TMA {init_data}")

    credentials = await tma_auth(mock_request)
    
    assert credentials is not None
    assert isinstance(credentials, HTTPTMACredentials)
    assert credentials.user_id == 123456789
    assert credentials.username == "test_user"
    assert credentials.language_code == "en"


async def test_expired_tma_init_data():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token, auto_error=False)
    
    expired_date = datetime.now(UTC) - timedelta(minutes=121)
    init_data = create_tma_init_data(bot_token, auth_date=expired_date)
    mock_request = create_mock_request(auth_header=f"TMA {init_data}")
    
    credentials = await tma_auth(mock_request)
    
    assert credentials is None


async def test_invalid_hash_tma_init_data():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token, auto_error=False)

    invalid_init_data = create_tma_init_data(bot_token=bot_token + "INVALID")
    mock_request = create_mock_request(auth_header=f"TMA {invalid_init_data}")
    
    credentials = await tma_auth(mock_request)
    
    assert credentials is None


async def test_missing_authorization_header():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token, auto_error=False)

    mock_request = create_mock_request()
    
    credentials = await tma_auth(mock_request)
    
    assert credentials is None


async def test_wrong_scheme():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token, auto_error=False)
    
    init_data = create_tma_init_data(bot_token)
    mock_request = create_mock_request(auth_header=f"Bearer {init_data}")
    
    credentials = await tma_auth(mock_request)
    
    assert credentials is None


async def test_auto_error_raises_exception():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token, auto_error=True)

    mock_request = create_mock_request()
    
    with pytest.raises(HTTPException) as exc_info:
        await tma_auth(mock_request)
    
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED


async def test_malformed_user_data():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token, auto_error=False)
    
    auth_timestamp = int(datetime.now(UTC).timestamp())
    malformed_user_data = "not_a_json"
    
    data_check_string = f"auth_date={auth_timestamp}\nuser={quote(malformed_user_data)}"
    secret_key = hmac.digest("WebAppData".encode("utf-8"), bot_token.encode('utf-8'), hashlib.sha256)  # noqa
    hash_value = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()  # noqa
    
    init_data = f"auth_date={auth_timestamp}&user={quote(malformed_user_data)}&hash={hash_value}"
    mock_request = create_mock_request(auth_header=f"TMA {init_data}")
    
    credentials = await tma_auth(mock_request)
    
    assert credentials is None


async def test_missing_user_fields():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token, auto_error=False)
    
    auth_timestamp = int(datetime.now(UTC).timestamp())
    incomplete_user_data = json.dumps({"id": 123456789})
    
    data_check_string = f"auth_date={auth_timestamp}\nuser={quote(incomplete_user_data)}"
    secret_key = hmac.digest("WebAppData".encode("utf-8"), bot_token.encode('utf-8'), hashlib.sha256)  # noqa
    hash_value = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()  # noqa
    
    init_data = f"auth_date={auth_timestamp}&user={quote(incomplete_user_data)}&hash={hash_value}"
    mock_request = create_mock_request(auth_header=f"TMA {init_data}")
    
    credentials = await tma_auth(mock_request)
    
    assert credentials is None


def test_make_authenticate_headers():
    bot_token = "test_bot_token_12345"
    tma_auth = HTTPTMAInitDataAuth(tg_bot_token=bot_token)
    
    headers = tma_auth.make_authenticate_headers()
    
    assert headers == {"WWW-Authenticate": "TMA"}
