from pydantic import Field

from .model import SchemeModel


class Genre(SchemeModel):
    name_en: str = Field(description="Genre name in English")
    name_uk: str = Field(description="Genre name in Ukrainian")