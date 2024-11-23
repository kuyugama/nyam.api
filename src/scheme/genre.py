from pydantic import Field

from .model import SchemeModel


class Genre(SchemeModel):
    name_en: str = Field(description="Назва жанру англійською")
    name_uk: str = Field(description="Назва жанру українською")
    slug: str = Field(description="Слаґ жанру")
