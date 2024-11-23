from src import constants
from tests import requests
from tests.helpers import assert_contain


async def test_none_chapter(client):
    response = await requests.content.list_pages(client, 1)
    print(response.json())
    assert response.status_code == 404

    assert_contain(response.json(), category="content/chapter", code="not-found")


async def test_none(client, chapter):
    response = await requests.content.list_pages(client, chapter.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(response.json(), pagination={"total": 0, "pages": 0, "page": 1}, items=[])


async def test_normal_image(client, chapter, page_image):
    response = await requests.content.list_pages(client, chapter.id)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}

    assert_contain(
        response.json()["items"][0],
        index=page_image.index,
    )

    assert_contain(
        response.json()["items"][0]["image"],
        width=page_image.image.width,
        height=page_image.image.height,
        mimetype=page_image.image.mime_type,
        url=page_image.image.url,
    )


async def test_normal_text(client, composition, chapter, page_text, session):
    composition.style = constants.STYLE_COMPOSITION_RANOBE
    await session.commit()

    response = await requests.content.list_pages(client, chapter.id)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}

    assert_contain(
        response.json()["items"][0],
        index=page_text.index,
        text=page_text.text,
    )
