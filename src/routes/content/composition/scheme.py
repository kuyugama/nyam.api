from pydantic import Field

from src.scheme import SchemeModel


class CreateCompositionVariantBody(SchemeModel):
    title: str | None = Field(
        None, min_length=3, max_length=255, description="Назва варіанту твору (необов'язково)"
    )
    synopsis: str | None = Field(
        None, min_length=3, max_length=4096, description="Опис варіанту твору (необов'язково)"
    )
