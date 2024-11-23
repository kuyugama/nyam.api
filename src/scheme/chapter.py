from pydantic import Field

from .model import Object


class Chapter(Object):
    index: int = Field(description="Порядковий номер цього розділу")
    title: str | None = Field(description="Назва цього розділу, може бути null")
    computed_title: str = Field(
        description="Обчислене поле назви цього розділу - '{{index}} | {{title}}'"
    )

    volume_id: int = Field(description="ID тому")

    pages: int = Field(description="Кількість сторінок у цьому розділі")
