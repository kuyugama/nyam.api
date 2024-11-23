from tests import requests
from tests.helpers import assert_composition, assert_contain


async def test_none(client):
    response = await requests.content.composition_by_slug(client, "slug")
    print(response.json())
    assert response.status_code == 404

    assert_contain(
        response.json(),
        code="composition-not-found",
        category="content/composition",
    )


async def test_normal(client, composition):
    response = await requests.content.composition_by_slug(client, composition.slug)
    print(response.json())
    assert response.status_code == 200

    assert_composition(response.json(), composition)
