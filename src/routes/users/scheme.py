from functools import partial
from operator import contains
from string import ascii_letters, digits

from pydantic import Field, field_validator

from src.util import consists_of
from src.scheme.model import SchemeModel
from src.permissions import permissions, permission_registry


class UpdateUserBody(SchemeModel):
    nickname: str | None = Field(None, description="User's nickname")
    pseudonym: str | None = Field(None, description="User's pseudonym")
    description: str | None = Field(None, description="User's description")
    remove_avatar: bool = Field(False, description="Whether to remove avatar")
    remove_pseudonym: bool = Field(False, description="Whether to remove pseudonym")
    remove_description: bool = Field(False, description="Whether to remove description")

    @field_validator("nickname")
    def validate_nickname(cls, v: str | None) -> str | None:
        if v is None:
            return None

        assert len(v) > 5, "Nickname length cannot be less than 5 characters"

        assert consists_of(
            v, ascii_letters + digits + "_"
        ), "Nickname can contain only ascii-letters, numbers and underscores"

        return v


class UpdateOtherUserBody(UpdateUserBody):
    permissions: dict[str, bool] | None = Field(
        None,
        examples=[{permissions.user.own.update_info: False}],
        description="User's permissions",
    )
    merge_permissions: bool = Field(False, description="Whether to merge permissions")

    @field_validator("permissions")
    def validate_permissions(cls, v: dict[str, bool] | None) -> dict[str, bool] | None:
        if v is None:
            return None

        assert all(map(partial(contains, permission_registry), v.keys())), "Bad permissions"

        return v
