import json
import hmac
import hashlib

from datetime import datetime, UTC
from urllib.parse import quote


def get_internal_auth_headers(user_id: int, username: str = "test_user", language_code: str = "en") -> dict:
    """ Helper function to generate INTERNAL authorization headers """
    user_data = json.dumps({"id": user_id, "username": username, "language_code": language_code})
    return {"Authorization": f"INTERNAL {user_data}"}


def create_tma_init_data(
    bot_token: str, user_id: int = 123456789, username: str = "test_user", language_code: str = "en",
    auth_date: datetime = None,
) -> str:
    """ Helper function to create valid TMA init data with correct hash """
    if auth_date is None:
        auth_date = datetime.now(UTC)

    auth_timestamp = int(auth_date.timestamp())
    user_data = json.dumps(
        {"id": user_id, "username": username, "language_code": language_code},
        separators=(',', ':')
    )

    data_check_string_parts = [
        f"auth_date={auth_timestamp}",
        f"user={user_data}",
        "signature=some_signature",
    ]
    data_check_string = "\n".join(sorted(data_check_string_parts))

    secret_key = hmac.digest(
        "WebAppData".encode("utf-8"),
        bot_token.encode('utf-8'),  # noqa
        hashlib.sha256
    )
    hash_value = hmac.new(
        secret_key,
        data_check_string.encode('utf-8'),  # noqa
        hashlib.sha256
    ).hexdigest()

    init_data = f"auth_date={auth_timestamp}&user={quote(user_data)}&signature=some_signature&hash={hash_value}"
    return init_data
