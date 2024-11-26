from tests import requests
from tests.helpers import assert_contain


async def test_none(client):
    response = await requests.content.get_page(client, 1)
    print(response.json())
    assert response.status_code == 404

    assert_contain(response.json(), category="content/page", code="not-found")


async def test_normal(client, page_image):
    response = await requests.content.get_page(client, page_image.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(response.json(), text=page_image.text, index=page_image.index)
