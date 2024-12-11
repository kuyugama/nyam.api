from pydantic import Field

from .team import Team
from .genre import Genre
from src import constants
from .image import UploadImage
from .model import Object, datetime_pd
from .team_member import TeamMemberWithoutTeam


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

    preview: UploadImage | None = Field(description="Composition preview")

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
    year: int | None = Field(description="Composition year")
    start_date: datetime_pd | None = Field(description="Composition start date")
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
    origin: Composition = Field(description="Оригінальний твір")

    team: Team = Field(description="Команда, що створила цей варіант твору")
    member: TeamMemberWithoutTeam = Field(
        description="Учасник команди, що створив цей варіант твору"
    )

    status: str = Field(
        description="Статус варіанту твору",
        examples=[
            constants.STATUS_COMPOSITION_VARIANT_PENDING,
            constants.STATUS_COMPOSITION_VARIANT_ABANDONED,
            constants.STATUS_COMPOSITION_VARIANT_COMPLETED,
        ],
    )

    title: str = Field(description="Назва варіанту твору (може відрізнятись від оригінальної)")
    synopsis: str = Field(description="Опис варіанту твору (може відрізнятись від оригінального)")

    # Cached fields
    chapters: int = Field(description="Кількість розділів варіанту твору")
    volumes: int = Field(description="Кількість томів варіанту твору")
