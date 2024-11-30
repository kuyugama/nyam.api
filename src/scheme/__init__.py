from pydantic import Field

from .user import User
from .role import Role
from .token import Token
from .model import Object
from .page import TextPage
from .volume import Volume
from .user import FullUser
from .page import ImagePage
from .error import APIError
from .chapter import Chapter
from .token import FullToken
from .error import ErrorModel
from .client import ClientInfo
from .model import SchemeModel
from .image import UploadImage
from .error import define_error
from .pagination import Paginated
from .providers import OAuthProvider
from .composition import Composition
from .providers import ContentProvider
from .error import ValidationErrorModel
from .error import define_error_category
from .composition import CompositionVariant


__all__ = [
    "Bot",
    "User",
    "Role",
    "Token",
    "Volume",
    "Object",
    "Chapter",
    "TextPage",
    "APIError",
    "FullUser",
    "ImagePage",
    "FullToken",
    "Paginated",
    "ClientInfo",
    "ErrorModel",
    "SchemeModel",
    "UploadImage",
    "Composition",
    "define_error",
    "OAuthProvider",
    "ContentProvider",
    "CompositionVariant",
    "ValidationErrorModel",
    "define_error_category",
]


class Bot(SchemeModel):
    name: str = Field(description="The name of the bot")
    description: str = Field(description="The description of the bot")
    contact: dict[str, str] = Field(
        description="Contact information of the owner", examples=[{"email": "<EMAIL>"}]
    )
