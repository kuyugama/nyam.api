from functools import lru_cache
from typing import Callable, Awaitable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src.util import check_permissions
from src.database import acquire_session
from .scheme import UpdateTeamBody, UpdateTeamMemberBody
from src.dependencies import require_token, master_grant
from src.models import Team, Token, TeamMember, TeamJoinRequest
from src.service import get_team_member, get_team, get_role_by_name

from .errors import (
    cannot_kick_highest_role,
    join_already_requested,
    provided_not_member,
    permission_denied,
    nothing_to_update,
    join_not_found,
    role_not_found,
    role_invalid,
    not_member,
    not_found,
)


_TeamResolver = Callable[..., Team | int | None | Awaitable[Team | int | None]]


@not_found.mark()
async def require_team(team_id: int, session: AsyncSession = Depends(acquire_session)) -> Team:
    team = await get_team(session, team_id)

    if team is None:
        raise not_found

    return team


@lru_cache()
def optional_team_member(resolve_team: _TeamResolver = require_team):

    @not_found.mark()
    async def dependency(
        team: int | Team | None = Depends(resolve_team),
        token: Token = Depends(require_token),
        session: AsyncSession = Depends(acquire_session),
    ) -> TeamMember | None:
        if team is None:
            raise not_found

        if isinstance(team, Team):
            team = team.id

        return await get_team_member(session, team, token.owner_id)

    return dependency


@lru_cache
def require_team_member(resolve_team: _TeamResolver = require_team):

    @not_found.mark()
    @not_member.mark()
    async def dependency(
        member: TeamMember | None = Depends(optional_team_member(resolve_team)),
    ):
        if member is None:
            raise not_member

        return member

    return dependency


@lru_cache
def require_team_permissions(*permissions, resolve_team: _TeamResolver = require_team):
    denied = permission_denied(extra=dict(permissions=", ".join(map(str, permissions))))

    @permission_denied.mark()
    async def dependency(
        team_member: TeamMember | None = Depends(optional_team_member(resolve_team)),
        master_granted: bool = Depends(master_grant),
    ):
        if master_granted:
            return

        # If team member does not exist or permission check failed
        if team_member is None or not check_permissions(permissions, team_member.permissions):
            raise denied

    return Depends(dependency)


@nothing_to_update.mark()
async def validate_update(
    body: UpdateTeamBody,
    team: Team = Depends(require_team),
):
    # If current details are the same - skip update
    if (
        body.name is not None
        and body.name == team.name
        and body.description is not None
        and body.description == team.description
    ):
        raise nothing_to_update

    return body


@join_not_found.mark()
async def require_team_join(
    join_id: int,
    team: Team = Depends(require_team),
    session: AsyncSession = Depends(acquire_session),
) -> TeamJoinRequest:
    join = await service.get_join(session, team, join_id)

    if join is None:
        raise join_not_found

    return join


@provided_not_member.mark()
async def require_provided_team_member(
    nickname: str,
    team: Team = Depends(require_team),
    session: AsyncSession = Depends(acquire_session),
):
    member = await service.get_team_member_by_nickname(session, team, nickname)

    if member is None:
        raise provided_not_member

    return member


@role_invalid.mark()
@role_not_found.mark()
async def validate_update_member(
    body: UpdateTeamMemberBody,
    session: AsyncSession = Depends(acquire_session),
):
    if body.role is not None:
        role = await get_role_by_name(session, body.role)
        if role is None:
            raise role_not_found

        if not role.team_member_role:
            raise role_invalid

    return body


@join_already_requested.mark()
async def require_no_join_request(
    team: Team = Depends(require_team),
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    join = await service.get_join_by_user(session, team, token.owner)
    if join is not None:
        raise join_already_requested


@cannot_kick_highest_role.mark()
async def validate_kick_member(
    member: TeamMember = Depends(require_provided_team_member),
    requester_member: TeamMember = Depends(optional_team_member()),
):
    # Cannot kick user with the highest role than requester user's role
    if requester_member is not None and requester_member.role.weight <= member.role.weight:
        raise cannot_kick_highest_role
