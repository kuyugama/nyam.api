import typing

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.dialects.postgresql import JSONB

from src.util import merge_permissions

if typing.TYPE_CHECKING:
    from .role import Role
    from .team_member import TeamMember
    from .team import Team


class _HasRoleAndLocalPermissions(typing.Protocol):
    role: "Role"
    local_permissions: dict[str, bool]


class PermissionMixin:
    # User individual permissions
    # Keys are actual permission names
    local_permissions: orm.Mapped[dict[str, bool]] = orm.mapped_column(
        MutableDict.as_mutable(typing.cast(TypeEngine, JSONB)), default={}
    )

    @property
    def permissions(self: _HasRoleAndLocalPermissions) -> dict[str, bool]:
        """Combine user's role and own permissions."""
        return merge_permissions(self.role.permissions, self.local_permissions)


# noinspection PyMethodParameters
class OwnedByTeamMixin:
    @orm.declared_attr
    def member_id(cls):
        return orm.mapped_column(sa.ForeignKey("service_team_members.id", ondelete="CASCADE"))

    @orm.declared_attr
    def member(cls) -> orm.Mapped["TeamMember"]:
        return orm.relationship(foreign_keys=[cls.member_id])

    @orm.declared_attr
    def team_id(cls):
        return orm.mapped_column(sa.ForeignKey("service_teams.id", ondelete="CASCADE"))

    @orm.declared_attr
    def team(cls) -> orm.Mapped["Team"]:
        return orm.relationship(foreign_keys=[cls.team_id])
