from tests import requests
from tests.helpers import assert_contain


async def test_without_title(client, token_admin, composition_variant):
    index = 1
    title = None
    response = await requests.content.create_volume(
        client, token_admin.body, composition_variant.id, index, title
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        index=index,
        computed_title=f"{index} | {title}" if title else str(index),
        chapters=0,
    )


async def test_title(client, token_admin, composition_variant):
    index = 1
    title = "title"
    response = await requests.content.create_volume(
        client, token_admin.body, composition_variant.id, index, title
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        index=index,
        computed_title=f"{index} | {title}" if title else str(index),
        chapters=0,
    )


async def test_autoindex(client, token_admin, composition_variant, volume):
    index = None
    title = None
    expected_index = volume.index + 1
    response = await requests.content.create_volume(
        client, token_admin.body, composition_variant.id, index, title
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        index=expected_index,
        computed_title=f"{expected_index} | {title}" if title else str(expected_index),
        chapters=0,
    )


async def test_insert(client, token_admin, composition_variant, volume, session):
    index = volume.index
    title = None
    response = await requests.content.create_volume(
        client, token_admin.body, composition_variant.id, index, title
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        index=index,
        computed_title=f"{index} | {title}" if title else str(index),
        chapters=0,
    )

    await session.refresh(volume)

    assert volume.index == index + 1
