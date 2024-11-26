from tests import requests
from tests.helpers import assert_contain


async def test_none_volume(client):
    response = await requests.content.list_chapters(client, 1)
    print(response.json())
    assert response.status_code == 404

    assert_contain(response.json(), category="content/volume", code="not-found")


async def test_none(client, volume):
    response = await requests.content.list_chapters(client, volume.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(response.json(), pagination={"total": 0, "pages": 0, "page": 1}, items=[])


async def test_normal(client, volume, chapter):
    response = await requests.content.list_chapters(client, volume.id)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}

    assert_contain(
        response.json()["items"][0],
        title=chapter.title,
        index=chapter.index,
        computed_title=chapter.computed_title,
        pages=chapter.pages,
    )
