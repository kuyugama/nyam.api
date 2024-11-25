from pydantic import Field

from .model import SchemeModel


class BaseProvider(SchemeModel):
    name: str = Field(description="Name of the provider")
    description: str = Field(description="Description of the provider")
    identifier: str = Field(description="Identifier of the provider")


class ContentProvider(BaseProvider):
    pass


class OAuthProvider(BaseProvider):
    pass
