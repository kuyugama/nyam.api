from tests import requests, data
from tests.helpers import MockedResponse

from unittest.mock import patch, AsyncMock


async def test_normal_composition(client):
    provider = "hikka"
    with patch("aiohttp.ClientSession") as mocked:
        instance = mocked.return_value
        instance.post = AsyncMock(
            return_value=MockedResponse(data.content_providers.search_onepiece)
        )

        response = await requests.content.search_composition_in_provider(
            client, provider, "onepiece"
        )
    print(response.json())
    assert response.status_code == 200

    response_data = response.json()

    assert (
        response_data["pagination"]["total"]
        == data.content_providers.search_onepiece["pagination"]["total"]
    )
    assert (
        response_data["pagination"]["pages"]
        == data.content_providers.search_onepiece["pagination"]["pages"]
    )
    assert (
        response_data["pagination"]["page"]
        == data.content_providers.search_onepiece["pagination"]["page"]
    )

    assert len(response_data["items"]) == len(data.content_providers.search_onepiece["list"])
