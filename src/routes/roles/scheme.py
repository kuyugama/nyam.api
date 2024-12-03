from functools import partial
from operator import contains

from pydantic import Field, field_validator

from src import scheme
from src.scheme import Paginated
from src.scheme.model import SchemeModel
from src.permissions import permission_registry


__all__ = [
    "FullRole",
    "Paginated",
    "CreateRoleBody",
    "UpdateRoleBody",
]

permissions_examples = [{key: True for key in permission_registry}]


class CreateRoleBody(SchemeModel):
    name: str = Field(max_length=128)
    base_role: str | None = Field(None)
    title: str = Field(max_length=512)
    weight: int | None = Field(None)
    default: bool = Field(False)
    permissions: dict[str, bool] = Field(
        examples=permissions_examples,
    )

    @field_validator("permissions")
    def validate_permissions(cls, v: dict[str, bool]) -> dict[str, bool]:
        assert all(map(partial(contains, permission_registry), v.keys())), "Bad permissions"

        return v


class UpdateRoleBody(SchemeModel):
    title: str | None = Field(max_length=512)
    default: bool | None = Field(default=False)
    weight: int | None = Field(default=None)
    permissions: dict[str, bool] | None = Field(examples=permissions_examples)
    merge_permissions: bool = Field(True, description="Whether to merge permissions")

    @field_validator("permissions")
    def validate_permissions(cls, v: dict[str, bool] | None) -> dict[str, bool] | None:
        if v is None:
            return v

        assert all(map(partial(contains, permission_registry), v.keys())), "Bad permission"

        return v


class FullRole(scheme.Role, scheme.Object):
    default: bool
    permissions: dict[str, bool] = Field(
        examples=permissions_examples,
        description="Role's permissions",
    )
