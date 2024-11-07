from pydantic import Field

from .model import SchemeModel


class ContentProvider(SchemeModel):
    name: str = Field(description="Name of the content provider")
    description: str = Field(description="Description of the content provider")
    identifier: str = Field(description="Identifier of the content provider")
