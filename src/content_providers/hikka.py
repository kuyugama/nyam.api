from collections.abc import Callable
from uuid import UUID

import aiohttp

from src import constants
from src.scheme import Paginated
from src.util.image_util import web_image_metadata
from .base import BaseContentProvider, ContentProviderComposition, SearchEntry


def _format_genres(genres: list[dict]) -> list[dict]:
    return [
        {
            "name_uk": genre["name_ua"],
            "name_en": genre["name_en"],
        }
        for genre in genres
    ]


def _format_status(status: str) -> str:
    match status:
        case "ongoing":
            return constants.STATUS_COMPOSITION_PENDING
        case "finished":
            return constants.STATUS_COMPOSITION_COMPLETED


def _format(composition: dict, field: str, formatter: Callable = None):
    if formatter is not None:
        composition[field] = formatter(composition[field])


def _rename(composition: dict, **kwargs):
    for new_name, name in kwargs.items():
        composition[new_name] = composition.pop(name)


class HikkaContentProvider(BaseContentProvider):
    async def parse_composition(self, identifier: str | int | UUID) -> ContentProviderComposition:
        client = aiohttp.ClientSession(self.endpoint)

        async with client:
            response = await client.get("/manga/{slug}".format(slug=identifier))

            composition = {
                "provider": "hikka",
                "provider_id": identifier,
            }

            composition.update(await response.json())

        _format(composition, "genres", _format_genres)
        _format(composition, "status", _format_status)
        _rename(composition, style="media_type", title_uk="title_ua", synopsis_uk="synopsis_ua")

        composition["preview"] = await web_image_metadata(composition["image"])

        return ContentProviderComposition.model_validate(composition)

    async def search_composition(self, query: str, page: int = 1):
        client = aiohttp.ClientSession(self.endpoint)

        async with client:
            response = await client.post("/manga", json={"query": query}, params={"page": page})

            response = await response.json()
            _rename(response, items="list")

            for composition in response["items"]:
                _rename(composition, style="media_type", title_uk="title_ua")
                _format(composition, "status", _format_status)
                composition.update({"provider": "hikka", "provider_id": composition["slug"]})

        return Paginated[SearchEntry].model_validate(response)
