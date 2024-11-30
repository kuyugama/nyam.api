import typing
from datetime import datetime, timedelta

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import ForeignKey
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base
from .role import Role
from src.util import now
from src import constants
from .image import UploadImage

__all__ = ["User"]

if typing.TYPE_CHECKING:
    from .token import Token


def _user_next_offline():
    return now() + timedelta(minutes=constants.USER_ONLINE_TTL)


class User(Base):
    # Sign-in columns
    # Email can be null only if user logged in by oauth
    email: orm.Mapped[str] = orm.mapped_column(index=True, nullable=True)
    # Public sign-in column (user can be found by it)
    nickname: orm.Mapped[str] = orm.mapped_column(index=True)
    password_hash: orm.Mapped[str] = orm.mapped_column(nullable=True)

    pseudonym: orm.Mapped[str] = orm.mapped_column(index=True, nullable=True)
    description: orm.Mapped[str] = orm.mapped_column(index=True, nullable=True)

    next_offline: orm.Mapped[datetime] = orm.mapped_column(
        index=True, default=_user_next_offline(), onupdate=_user_next_offline
    )

    avatar_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey(UploadImage.id, ondelete="SET NULL"), nullable=True
    )
    avatar: orm.Mapped[UploadImage] = orm.relationship(UploadImage, foreign_keys=[avatar_id])

    tokens: orm.Mapped[list["Token"]] = orm.relationship("Token", back_populates="owner")

    role_id = orm.mapped_column(ForeignKey(Role.id, ondelete="CASCADE"))
    role: orm.Mapped[Role] = orm.relationship(Role, foreign_keys=[role_id])

    # User individual permissions
    # Keys are actual permission names
    local_permissions: orm.Mapped[dict[str, bool]] = orm.mapped_column(
        MutableDict.as_mutable(JSONB), default={}  # type: ignore
    )

    @property
    def permissions(self):
        """Combine user's role and own permissions."""
        return self.role.permissions | self.local_permissions

    @property
    def online(self):
        return now() < self.next_offline

    def prolong_online(self):
        self.next_offline = _user_next_offline()
