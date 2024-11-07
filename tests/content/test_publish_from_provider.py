from tests import requests, data
from tests.helpers import MockedResponse

from unittest.mock import patch, AsyncMock


async def test_normal_composition(client):
    provider = "hikka"
    with patch("aiohttp.ClientSession") as mocked_client:
        instance = mocked_client.return_value
        instance.post = AsyncMock(
            return_value=MockedResponse(data.content_providers.search_onepiece)
        )
        response = await requests.content.search_composition_in_provider(
            client, provider, "onepiece"
        )

    print(response.json(), end="\n\n")
    assert response.status_code == 200

    provider_id = response.json()["items"][0]["provider_id"]

    with (
        patch(
            "src.content_providers.hikka.web_image_metadata",
        ) as mocked_image_metadata,
        patch("aiohttp.ClientSession") as mocked_client,
    ):
        mocked_image_metadata.return_value = data.util.web_image_metadata

        mocked_client.return_value.get = AsyncMock(
            return_value=MockedResponse(data.content_providers.parse_onepiece)
        )

        response = await requests.content.publish_composition_from_provider(
            client, provider, provider_id
        )
    print(response.json())
    assert response.status_code == 200
