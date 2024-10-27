from pydantic import Field

from src.scheme.model import SchemeModel


class Role(SchemeModel):
    name: str = Field(examples=["user"], description="Name of the role")
    title: str = Field(description="Title of the role")
