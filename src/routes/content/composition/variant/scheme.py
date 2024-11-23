from pydantic import Field

from src.scheme import SchemeModel


class CreateVolumeBody(SchemeModel):
    index: int | None = Field(
        None,
        description="Порядковий номер тому, необов'язкове значення, "
        "якщо не вказано створиться автоматично",
    )

    title: str | None = Field(
        None, max_length=255, min_length=3, description="Назва тому, необов'язкове значення"
    )
