from contextlib import contextmanager
from unittest.mock import patch

from src import constants
from tests import requests
from tests.helpers import assert_contain


@contextmanager
def _patch_s3():
    with patch("src.routes.content.chapter.service.upload_file_obj"):
        yield


async def test_text(client, token_translator, composition, chapter, session):
    composition.style = constants.STYLE_COMPOSITION_RANOBE
    await session.commit()

    text = "page text" * 100
    index = 1
    response = await requests.content.create_text_page(
        client, token_translator.body, chapter.id, text, index
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        text=text,
        index=index,
    )


async def test_image(client, token_translator, image_file, chapter, session):
    index = 1
    with _patch_s3():
        response = await requests.content.create_image_page(
            client, token_translator.body, chapter.id, image_file, index
        )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        index=index,
    )


async def test_text_autoindex(client, token_translator, composition, chapter, page_text, session):
    composition.style = constants.STYLE_COMPOSITION_RANOBE
    await session.commit()

    text = "page text" * 100
    index = None
    expected_index = page_text.index + 1
    response = await requests.content.create_text_page(
        client, token_translator.body, chapter.id, text, index
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        text=text,
        index=expected_index,
    )


async def test_image_autoindex(client, token_translator, image_file, chapter, page_image, session):
    index = None
    expected_index = page_image.index + 1
    with _patch_s3():
        response = await requests.content.create_image_page(
            client, token_translator.body, chapter.id, image_file, index
        )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        index=expected_index,
    )


async def test_text_insert(client, token_translator, composition, chapter, page_text, session):
    composition.style = constants.STYLE_COMPOSITION_RANOBE
    await session.commit()

    text = "page text" * 100
    index = page_text.index
    response = await requests.content.create_text_page(
        client, token_translator.body, chapter.id, text, index
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        text=text,
        index=index,
    )

    await session.refresh(page_text)

    assert page_text.index == index + 1


async def test_image_insert(client, token_translator, chapter, image_file, page_image, session):
    index = page_image.index
    with _patch_s3():
        response = await requests.content.create_image_page(
            client, token_translator.body, chapter.id, image_file, index
        )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        index=index,
    )
