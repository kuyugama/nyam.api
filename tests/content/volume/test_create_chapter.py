from tests import requests
from tests.helpers import assert_contain


async def test_without_title(client, token_translator, volume):
    index = 1
    title = None
    response = await requests.content.create_chapter(
        client, token_translator.body, volume.id, index, title
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        index=index,
        computed_title=f"{index} | {title}" if title else str(index),
        pages=0,
    )


async def test_title(client, token_translator, volume):
    index = 1
    title = "title"
    response = await requests.content.create_chapter(
        client, token_translator.body, volume.id, index, title
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        index=index,
        computed_title=f"{index} | {title}" if title else str(index),
        pages=0,
    )


async def test_autoindex(client, token_translator, volume, chapter):
    index = None
    title = None
    expected_index = chapter.index + 1
    response = await requests.content.create_chapter(
        client, token_translator.body, volume.id, index, title
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        index=expected_index,
        computed_title=f"{expected_index} | {title}" if title else str(expected_index),
        pages=0,
    )


async def test_insert(client, token_translator, volume, chapter, session):
    index = chapter.index
    title = None
    response = await requests.content.create_chapter(
        client, token_translator.body, volume.id, index, title
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        index=index,
        computed_title=f"{index} | {title}" if title else str(index),
        pages=0,
    )

    await session.refresh(chapter)

    assert chapter.index == index + 1
