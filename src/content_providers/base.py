from uuid import UUID
from datetime import datetime
from abc import ABC, abstractmethod

from pydantic import Field

from src.scheme import Paginated, SchemeModel


class ContentProviderImageMetadata(SchemeModel):
    url: str
    height: int
    width: int
    mimetype: str


class ContentProviderComposition(SchemeModel):
    slug: str

    style: str

    # Titles
    title_original: str
    title_en: str | None = None
    title_uk: str | None = None

    # Synopses
    synopsis_en: str | None = None
    synopsis_uk: str | None = None

    # Other fields
    status: str
    year: int | None
    start_date: datetime | None
    nsfw: bool
    genres: list[dict]
    tags: list[str] = Field(default_factory=list)
    chapters: int | None
    volumes: int | None

    preview: ContentProviderImageMetadata | None

    # MyAnimeList id
    mal_id: int | None = None

    # Content provider name
    provider: str
    # Resource id at content provider
    provider_id: str


class SearchEntry(SchemeModel):
    slug: str
    title_original: str
    title_uk: str | None
    title_en: str | None
    style: str
    chapters: int | None
    volumes: int | None
    status: str
    image: str
    year: int | None

    provider: str
    provider_id: str


class BaseContentProvider(ABC):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    @abstractmethod
    async def parse_composition(self, identifier: str) -> ContentProviderComposition:
        raise NotImplementedError

    @abstractmethod
    async def search_composition(
        self, query: str, page: int = 0
    ) -> Paginated[ContentProviderComposition]:
        raise NotImplementedError
