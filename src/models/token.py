from datetime import datetime, timedelta

import sqlalchemy as sa
import sqlalchemy.orm as orm

from .base import Base
from .user import User
from src.util import now
from .. import constants


class Token(Base):
    owner_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(User.id, ondelete="CASCADE"))
    owner: orm.Mapped[User] = orm.relationship(foreign_keys=[owner_id], back_populates="tokens")

    body: orm.Mapped[str] = orm.mapped_column(index=True)
    expire_at: orm.Mapped[datetime]

    used_at: orm.Mapped[datetime] = orm.mapped_column(index=True, nullable=True)

    @property
    def token(self):
        return self.body

    def expired(self) -> bool:
        return now() >= self.expire_at

    def use(self):
        self.used_at = now()

    def prolong(self):
        if self.expire_at - now() < timedelta(seconds=constants.TOKEN_PROLONG_INTERVAL):
            return

        self.expire_at = now() + timedelta(seconds=constants.TOKEN_TTL)
