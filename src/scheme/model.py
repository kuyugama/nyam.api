from datetime import timedelta, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer, Field

from src.util import utc_timestamp

datetime_pd = Annotated[
    datetime,
    PlainSerializer(
        lambda x: x and int(utc_timestamp(x)),
        return_type=int,
    ),
]

timedelta_pd = Annotated[
    timedelta,
    PlainSerializer(
        lambda x: int(x.total_seconds()),
        return_type=int,
    ),
]


class SchemeModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
        validate_default=True,
    )


class Object(SchemeModel):
    id: int

    created_at: datetime_pd = Field(description="Дата та час створення об'єкту")
    updated_at: datetime_pd | None = Field(
        None, description="Дата та час останнього оновлення об'єкту"
    )
