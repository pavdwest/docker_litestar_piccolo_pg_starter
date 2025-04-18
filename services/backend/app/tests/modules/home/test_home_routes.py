from httpx import AsyncClient
from litestar import status_codes


async def test_index(client: AsyncClient):
    response = await client.get(
        '/home',
    )
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == {
        'message': 'Hello boils and ghouls.'
    }
