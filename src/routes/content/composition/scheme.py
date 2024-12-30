from pydantic import Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from src import util
from src.scheme import SchemeModel


class CreateCompositionVariantBody(SchemeModel):
    title: str | None = Field(
        None, min_length=3, max_length=255, description="Назва варіанту твору (необов'язково)"
    )
    synopsis: str | None = Field(
        None, min_length=3, max_length=4096, description="Опис варіанту твору (необов'язково)"
    )
    team_id: int = Field(description="Від імені якої команди створити варіант твору (обов'язково)")


class CompositionListBody(SchemeModel):
    genres: list[str] | None = Field(None, description="Перелік жанрів")
    genres_exclude: list[str] | None = Field(
        None, description="Перелік жанрів, які не потрібно включати"
    )
    tags: list[str] | None = Field(None, description="Перелік теґів")
    tags_exclude: list[str] | None = Field(
        None, description="Перелік теґів, які не потрібно включати"
    )
    styles: list[str] | None = Field(None, description="Перелік стилів")
    nsfw: bool | None = Field(None, description="NSFW, або не NSFW твори. null - не звертати уваги")

    years: tuple[int, int] | None = Field(None, description="Роки. [Від, До]")
    volumes: tuple[int, int] | None = Field(None, description="Кількість томів. [Від, До]")
    chapters: tuple[int, int] | None = Field(None, description="Кількість розділів. [Від, До]")

    @field_validator("genres")
    def validate_genres(cls, v: list[str] | None) -> list[str] | None:
        if not v:
            return None

        return util.lower(v)

    @field_validator("years", "volumes", "chapters")
    def validate_range_fields(cls, v: tuple[int, int] | None) -> tuple[int, int] | None:
        if v is None:
            return v

        if v[0] > v[1]:
            return v[1], v[0]

        return v

    @field_validator("genres_exclude", "tags_exclude")
    def validate_exclude_fields(cls, v: list[str] | None, info: ValidationInfo) -> list[str] | None:
        if not v:
            return None

        depend_field_name = info.field_name.split("_", 1)[0]
        depend_field = info.data.get(depend_field_name)

        assert not (
            depend_field and not set(v).intersection(set(depend_field))
        ), f"Genres present in '{info.field_name}' field cannot be present in '{depend_field_name}' field"

        return v

    def cache_key(self) -> tuple:
        return (
            self.nsfw,
            self.tags,
            self.years,
            self.genres,
            self.styles,
            self.volumes,
            self.chapters,
            self.tags_exclude,
            self.genres_exclude,
        )
