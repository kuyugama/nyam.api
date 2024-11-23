from tests import requests
from tests.helpers import assert_contain


async def test_none(client):
    response = await requests.content.get_chapter(client, 1)
    print(response.json())
    assert response.status_code == 404

    assert_contain(response.json(), category="content/chapter", code="not-found")


async def test_normal(client, chapter):
    response = await requests.content.get_chapter(client, chapter.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=chapter.title,
        index=chapter.index,
        computed_title=chapter.computed_title,
        pages=chapter.pages,
    )
