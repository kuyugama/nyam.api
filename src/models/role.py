import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base


class Role(Base):
    name: orm.Mapped[str] = orm.mapped_column(sa.String(128), index=True, unique=True)
    title: orm.Mapped[str]
    weight: orm.Mapped[int] = orm.mapped_column(server_default="0", index=True)
    default: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)

    # Is this role for team member
    team_member_role: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)

    # Role permissions
    # Keys are actual permission names
    permissions: orm.Mapped[dict[str, bool]] = orm.mapped_column(
        MutableDict.as_mutable(JSONB), default={}  # type: ignore
    )
