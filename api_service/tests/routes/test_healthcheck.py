from fastapi import status
from httpx import AsyncClient


async def test_healthcheck(async_client: AsyncClient) -> None:
    response = await async_client.get('/healthcheck')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'ok'}
