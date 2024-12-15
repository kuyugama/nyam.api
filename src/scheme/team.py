from pydantic import Field

from .model import Object


class Team(Object):
    name: str = Field(description="Назва команди")
    description: str = Field(description="Опис команди")
    verified: bool = Field(description="Верифікація команди")

    members: int = Field(description="Кількість учасників команди")
    variants: int = Field(description="Кількість перекладених творів командою")
    rating: int = Field(description="Глобальний рейтинг команди")
    rated_by: int = Field(description="Кількість людей, що оцінили роботу команди")
