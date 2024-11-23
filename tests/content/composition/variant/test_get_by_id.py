from tests import requests
from tests.helpers import assert_contain


async def test_none(client):
    response = await requests.content.get_composition_variant(client, 0)
    print(response.json())
    assert response.status_code == 404

    assert response.json()["category"] == "content/composition/variant"
    assert response.json()["code"] == "not-found"


async def test_normal(client, composition_variant):
    response = await requests.content.get_composition_variant(client, composition_variant.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=composition_variant.title,
        synopsis=composition_variant.synopsis,
        volumes=composition_variant.volumes,
        chapters=composition_variant.chapters,
    )
