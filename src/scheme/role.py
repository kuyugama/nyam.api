from pydantic import Field

from src.scheme.model import SchemeModel


class Role(SchemeModel):
    name: str = Field(examples=["user"], description="Назва ролі")
    title: str = Field(description="Опис ролі")
    weight: int = Field(description="Вага ролі")
