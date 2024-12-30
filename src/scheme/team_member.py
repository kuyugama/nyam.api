from pydantic import Field

from .team import Team
from .role import Role
from .user import User
from .model import Object


class TeamMemberWithoutTeam(Object):
    pseudonym: str | None = Field(description="Псевдонім учасника команди")
    user: User = Field(description="Користувач, що є учасником команди")
    role: Role = Field(description="Роль учасника команди")
    permissions: dict[str, bool] = Field(description="Дозволи учасника команди")


class TeamMember(TeamMemberWithoutTeam):
    team: Team = Field(description="Команда, якій належить учасник")
