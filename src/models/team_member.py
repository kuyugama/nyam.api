from sqlalchemy import orm, ForeignKey

from .base import Base

from .team import Team
from .user import User
from .role import Role
from .mixins import PermissionMixin


class TeamMember(Base, PermissionMixin):
    __tablename__ = "service_team_members"

    pseudonym: orm.Mapped[str] = orm.mapped_column(nullable=True)

    user_id = orm.mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    user: orm.Mapped[User] = orm.relationship(foreign_keys=[user_id])

    team_id = orm.mapped_column(ForeignKey(Team.id, ondelete="CASCADE"))
    team: orm.Mapped[Team] = orm.relationship(foreign_keys=[team_id])

    role_id = orm.mapped_column(ForeignKey(Role.id, ondelete="CASCADE"))
    role: orm.Mapped[Role] = orm.relationship(foreign_keys=[role_id])

    # Cached fields
    variants: orm.Mapped[int] = orm.mapped_column(default=0, index=True)
