from pydantic import BaseModel, Field


class PublishTextPageBody(BaseModel):
    index: int | None = Field(
        None,
        description="Порядковий номер сторінки, необов'язкове значення, "
        "якщо не вказано створиться автоматично",
    )
    text: str = Field(min_length=128, max_length=8192)
