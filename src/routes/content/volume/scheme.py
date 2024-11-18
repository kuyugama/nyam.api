from pydantic import Field

from src.scheme import SchemeModel


class CreateChapterBody(SchemeModel):
    index: int | None = Field(
        None,
        description="Порядковий номер розділу, необов'язкове значення, "
        "якщо не вказано створиться автоматично",
    )
    title: str | None = Field(
        None, min_length=3, max_length=255, description="Назва розділу, необов'язкове значення"
    )
