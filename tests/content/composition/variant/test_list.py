from tests import requests
from tests.helpers import assert_contain


async def test_composition_none(client):
    response = await requests.content.list_composition_variants(client, "slug")
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 0, "pages": 0, "page": 1}

    assert response.json()["items"] == []


async def test_none(client, composition):
    response = await requests.content.list_composition_variants(client, composition.slug)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 0, "pages": 0, "page": 1}

    assert response.json()["items"] == []


async def test_normal(client, composition_variant):
    response = await requests.content.list_composition_variants(
        client, composition_variant.origin.slug
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}

    assert_contain(
        response.json()["items"][0],
        title=composition_variant.title,
        synopsis=composition_variant.synopsis,
        volumes=composition_variant.volumes,
        chapters=composition_variant.chapters,
    )
