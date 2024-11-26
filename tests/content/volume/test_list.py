from tests import requests
from tests.helpers import assert_contain


async def test_none_variant(client):
    response = await requests.content.list_volumes(client, 1)
    print(response.json())
    assert response.status_code == 404

    assert_contain(response.json(), category="content/composition/variant", code="not-found")


async def test_none(client, composition_variant):
    response = await requests.content.list_volumes(client, composition_variant.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(response.json(), pagination={"total": 0, "pages": 0, "page": 1}, items=[])


async def test_normal(client, composition_variant, volume):
    response = await requests.content.list_volumes(client, composition_variant.id)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}

    assert_contain(
        response.json()["items"][0],
        title=volume.title,
        index=volume.index,
        computed_title=volume.computed_title,
        chapters=volume.chapters,
    )
