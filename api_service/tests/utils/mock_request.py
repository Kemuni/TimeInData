from fastapi import Request
from unittest.mock import Mock


def create_mock_request(
        headers: dict = None,
        auth_header: str = "",
        ip_address: str = "127.0.0.1"
) -> Request:
    """ Helper function to create the mock request object for testing """
    mock_request = Mock(spec=Request)
    mock_request.headers = headers or {}
    if auth_header:
        mock_request.headers["Authorization"] = auth_header
    mock_request.client.host = ip_address
    return mock_request
