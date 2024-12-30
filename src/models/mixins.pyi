import sqlalchemy as sa
from sqlalchemy import orm

from .team_member import TeamMember
from .team import Team

class PermissionMixin:
    local_permissions: dict[str, bool]

    @property
    def permissions(self) -> dict[str, bool]: ...

class OwnedByTeamMixin:
    team_id: orm.Mapped[int] = orm.mapped_column()
    team: orm.Mapped[Team] = orm.mapped_column()

    member_id: orm.Mapped[int] = orm.mapped_column()
    member: orm.Mapped[TeamMember] = orm.mapped_column()
