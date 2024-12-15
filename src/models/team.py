from sqlalchemy import orm, ForeignKey

from .user import User
from .base import Base
from .. import constants


class Team(Base):
    __tablename__ = "service_teams"

    name: orm.Mapped[str] = orm.mapped_column(index=True)
    description: orm.Mapped[str] = orm.mapped_column(index=True)
    verified: orm.Mapped[bool] = orm.mapped_column(index=True, default=False)

    # Cached fields
    members: orm.Mapped[int] = orm.mapped_column(default=0, index=True)
    variants: orm.Mapped[int] = orm.mapped_column(default=0, index=True)
    rating: orm.Mapped[int] = orm.mapped_column(default=0, index=True)
    rated_by: orm.Mapped[int] = orm.mapped_column(default=0, index=True)


class TeamJoinRequest(Base):
    __tablename__ = "service_team_join_requests"
    team_id = orm.mapped_column(ForeignKey(Team.id))
    team: orm.Mapped[Team] = orm.relationship(foreign_keys=[team_id])

    user_id = orm.mapped_column(ForeignKey(User.id))
    user: orm.Mapped[User] = orm.relationship(foreign_keys=[user_id])

    status: orm.Mapped[str] = orm.mapped_column(
        default=constants.STATUS_TEAM_JOIN_PENDING, index=True
    )
