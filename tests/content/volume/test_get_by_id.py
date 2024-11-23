from tests import requests
from tests.helpers import assert_contain


async def test_none(client):
    response = await requests.content.get_volume(client, 1)
    print(response.json())
    assert response.status_code == 404

    assert_contain(response.json(), category="content/volume", code="not-found")


async def test_normal(client, volume):
    response = await requests.content.get_volume(client, volume.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=volume.title,
        index=volume.index,
        computed_title=volume.computed_title,
        chapters=volume.chapters,
    )
