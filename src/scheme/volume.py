from pydantic import Field

from .model import Object


class Volume(Object):
    index: int = Field(description="Порядковий номер цього тому")
    title: str | None = Field(description="Назва цього тому, може бути null")
    computed_title: str = Field(
        description="Обчислене поле назви цього тому - '{{index}} | {{title}}'"
    )

    variant_id: int = Field(description="ID варіанту твору")

    chapters: int = Field(description="Кількість розділів у цьому томі")
