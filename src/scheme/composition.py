from pydantic import Field

from .user import User
from .genre import Genre
from .model import Object
from src import constants
from .image import UploadImage


class Composition(Object):
    slug: str = Field(description="Composition slug")

    style: str = Field(
        description="Composition style",
        examples=[
            constants.STYLE_COMPOSITION_MANGA,
            constants.STYLE_COMPOSITION_MANHUA,
            constants.STYLE_COMPOSITION_MANHWA,
            constants.STYLE_COMPOSITION_RANOBE,
        ],
    )

    preview: UploadImage = Field(description="Composition preview")

    # Titles
    title_original: str | None = Field(description="Original composition title")
    title_en: str | None = Field(description="Composition title in English")
    title_uk: str | None = Field(description="Composition title in Ukrainian")
    title: str | None = Field(description="Composition title")

    # Synopses
    synopsis_en: str | None = Field(description="Composition synopsis in English")
    synopsis_uk: str | None = Field(description="Composition synopsis in Ukrainian")
    synopsis: str | None = Field(description="Composition synopsis")

    # Other fields
    status: str = Field(
        description="Composition status",
        examples=[constants.STATUS_COMPOSITION_PENDING, constants.STATUS_COMPOSITION_COMPLETED],
    )
    year: int = Field(description="Composition year")
    nsfw: bool = Field(description="Is composition nsfw")
    genres: list[Genre] = Field(description="Composition genres")
    tags: list[str] = Field(description="Composition tags")
    chapters: int | None = Field(description="Composition chapters")
    volumes: int | None = Field(description="Composition volumes")

    # MyAnimeList id
    mal_id: int | None = Field(description="Composition MyAnimeList ID")

    # Content provider name
    provider: str | None = Field(description="Content provider")
    # Resource id at content provider
    provider_id: str | None = Field(description="Resource ID at content provider")

    # Cached fields
    variants: int = Field(description="Composition translations count")
    score: float = Field(description="Composition score")
    scored_by: int = Field(description="Composition scored by users count")


class CompositionVariant(Object):
    origin: Composition = Field(description="Original composition")

    author: User = Field(description="Compositon variant author")

    status: str = Field(
        description="Composition variant status",
        examples=[
            constants.STATUS_COMPOSITION_VARIANT_PENDING,
            constants.STATUS_COMPOSITION_VARIANT_ABANDONED,
            constants.STATUS_COMPOSITION_VARIANT_COMPLETED,
        ],
    )

    title: str = Field(description="Composition variant title")
    synopsis: str = Field(description="Composition variant synopsis")

    # Cached fields
    chapters: int = Field(description="Composition variant chapters")
    volumes: int = Field(description="Composition variant volumes")
