from functools import partial
from operator import contains

from pydantic import Field, field_validator

from src import constants
from src.permissions import team_permission_registry
from src.scheme import Object, SchemeModel, User, Team


class CreateTeamBody(SchemeModel):
    name: str = Field(min_length=3, max_length=128, description="Назва команди")
    description: str = Field(max_length=1024, description="Опис команди")


class UpdateTeamBody(SchemeModel):
    name: str | None = Field(min_length=3, max_length=128, description="Назва команди")
    description: str | None = Field(max_length=1028, description="Опис команди")


class UpdateTeamMemberBody(SchemeModel):
    pseudonym: str | None = Field(
        None, min_length=3, max_length=64, description="Встановити псевдонім учаснику"
    )
    role: str | None = Field(None, description="Встановити роль учаснику")
    permissions: dict[str, bool] | None = Field(None, description="Встановити дозволи учаснику")
    permissions_merge: bool = Field(
        False, description="Об'єднати передані дозволи з вже встановленими"
    )

    @field_validator("permissions")
    def validate_permissions(cls, value: dict[str, bool] | None) -> dict[str, bool] | None:
        if not value:  # Empty list or null
            return None

        assert all(
            map(partial(contains, team_permission_registry), value.keys())
        ), "Bad permissions"

        return value


class TeamJoinRequest(Object):
    user: User = Field(description="Користувач, що намагається приєднатись до команди")
    team: Team = Field(description="Команда до якої намагаються приєднатись")
    status: str = Field(
        constants.STATUS_TEAM_JOIN_PENDING,
        examples=[
            constants.STATUS_TEAM_JOIN_PENDING,
            constants.STATUS_TEAM_JOIN_ACCEPTED,
            constants.STATUS_TEAM_JOIN_REJECTED,
        ],
        description="Статус запиту очікує/схвалено/відмовлено",
    )
