from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import constants
from src.models import Role
from src.util import merge_permissions
from src.permissions import permissions, team_permissions

DEFAULT_ROLES = {
    constants.ROLE_TEAM_OWNER: {
        "team_member_role": True,
        "weight": 50,
        "title": "Власник команди",
        "permissions": {
            team_permissions.content_variant.__: True,
            team_permissions.volume.__: True,
            team_permissions.chapter.__: True,
            team_permissions.page.__.__: True,
            team_permissions.team.disband: True,
            team_permissions.team.update: True,
            team_permissions.member.manage_roles: True,
            team_permissions.member.manage_permissions: True,
            team_permissions.join.list: True,
            team_permissions.join.accept: True,
            team_permissions.join.reject: True,
        },
    },
    constants.ROLE_TEAM_MEMBER: {
        "team_member_role": True,
        "weight": 0,
        "title": "Учасник команди",
        "permissions": {
            team_permissions.volume.create: True,
            team_permissions.chapter.create: True,
            team_permissions.page.__.create: True,
        },
    },
    constants.ROLE_ROOT: {
        "team_member_role": False,
        "weight": 666,
        "title": "Той, кого не кличуть",
        "permissions": {permissions.__: True},
    },
    constants.ROLE_ADMINISTRATOR: {
        "team_member_role": False,
        "weight": 50,
        "title": "Адміністратор",
        "permissions": {
            permissions.content.__.__: True,
            permissions.user.permission_management: True,
        },
    },
    constants.ROLE_MODERATOR: {
        "team_member_role": False,
        "weight": 40,
        "title": "Модератор",
        "permissions": {
            permissions.content.__.delete: True,
            permissions.user.update_info: True,
        },
    },
    constants.ROLE_PUBLISHER: {
        "propagate": False,
        "team_member_role": False,
        "weight": 30,
        "title": "Видавець",
        "permissions": {
            permissions.content.__.publish: True,
            permissions.content.__.update: True,
            permissions.content.__.delete: True,
        },
    },
    constants.ROLE_USER: {
        "team_member_role": False,
        "weight": 20,
        "title": "Користувач",
        "permissions": {
            permissions.user.own.update_info: True,
        },
    },
    constants.ROLE_UNVERIFIED: {
        "team_member_role": False,
        "weight": 0,
        "title": "Не верифікований",
        "permissions": {},
    },
}

# Roles with propagated permissions from lower to higher weight
SORTED_ROLES = {}

_prev_role = None
# Sort roles by weight and team_member_role parameter
for _role_name in sorted(
    DEFAULT_ROLES,
    key=lambda x: DEFAULT_ROLES[x]["weight"]
    + (1000 if DEFAULT_ROLES[x]["team_member_role"] else 0),
):
    _role = DEFAULT_ROLES[_role_name].copy()
    # If previous role is not none and is for same group of users (users or team_members)
    if _prev_role is not None and _prev_role["team_member_role"] == _role["team_member_role"]:
        _role["permissions"] = merge_permissions(_prev_role["permissions"], _role["permissions"])

    # Not propagate permissions if "propagate" set to False
    if _role.get("propagate", True):
        _prev_role = _role

    SORTED_ROLES[_role_name] = {
        "team_member_role": _role["team_member_role"],
        "weight": _role["weight"],
        "title": _role["title"],
        "permissions": _role["permissions"],
    }


async def create_default_roles(session: AsyncSession):
    """
    Create default roles.
    """

    unique_names = set(DEFAULT_ROLES)
    names_to_add = unique_names.difference(
        (await session.scalars(select(Role.name).filter(Role.name.in_(DEFAULT_ROLES.keys())))).all()
    )

    for name in names_to_add:
        role = Role(
            name=name,
            title=SORTED_ROLES[name]["title"],
            weight=SORTED_ROLES[name]["weight"],
            permissions={
                str(permission): allowed
                for permission, allowed in SORTED_ROLES[name]["permissions"].items()
            },
        )
        session.add(role)

    if names_to_add:
        await session.commit()
        print("Added default roles:", *names_to_add)
