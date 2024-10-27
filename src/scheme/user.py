from pydantic import EmailStr, Field

from .role import Role
from .model import Object
from src import permissions
from .image import UploadImage


class User(Object):
    nickname: str = Field(description="User's nickname")

    pseudonym: str | None = Field(description="User's pseudonym")
    description: str | None = Field(description="User's description")

    avatar: UploadImage | None = Field(description="User's avatar")

    role: Role | None = Field(description="User's role")

    online: bool = Field(description="User's online status")

    permissions: dict[str, bool] = Field(
        examples=[{permissions.user.own.update_info: True}],
        description="User's permissions",
    )


class FullUser(User):
    email: EmailStr = Field(description="User's email")
