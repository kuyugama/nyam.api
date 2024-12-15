from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, ScalarResult, Select

from src import constants
from src.util import merge_permissions
from src.service import get_role_by_name
from src.models import Team, User, TeamMember, Role, TeamJoinRequest
from .scheme import CreateTeamBody, UpdateTeamBody, UpdateTeamMemberBody


# region Team


def filter_teams(query: Select, member: User | None = None) -> Select:
    if member is not None:
        query = query.filter(
            Team.id == TeamMember.team_id,  # type: ignore
            TeamMember.user_id == member.id,
        )

    return query


async def count_teams(session: AsyncSession, member: User | None = None) -> int:
    return await session.scalar(filter_teams(select(func.count(Team.id)), member))


async def list_teams(
    session: AsyncSession, offset: int, limit: int, member: User | None = None
) -> ScalarResult[Team]:
    return await session.scalars(
        filter_teams(
            select(Team)
            .order_by(Team.rating.desc(), Team.verified.desc(), Team.created_at.desc())
            .offset(offset)
            .limit(limit),
            member,
        )
    )


async def create_team(session: AsyncSession, body: CreateTeamBody, owner: User) -> Team:
    team = Team(
        name=body.name,
        description=body.description,
    )

    # Find role with higher weight for team member and set it for team owner
    owner_role = await session.scalar(
        select(Role).filter(Role.team_member_role).order_by(Role.weight.desc()).limit(1)
    )

    owner = TeamMember(
        team=team,
        user=owner,
        role=owner_role,
    )
    session.add_all([team, owner])
    await session.commit()

    return team


async def update_team(session: AsyncSession, team: Team, body: UpdateTeamBody):
    if body.name:
        team.name = body.name

    if body.description:
        team.description = body.description

    await session.commit()

    return team


# endregion

# region Team Members


def filter_members(query: Select, team: Team) -> Select:
    return query.filter(
        TeamMember.team_id == team.id,
    )


def members_options(query: Select) -> Select:
    return query.options(
        joinedload(
            TeamMember.team,
        ),
        joinedload(TeamMember.user).options(
            joinedload(User.avatar, User.role),
        ),
        joinedload(TeamMember.role),
    )


async def count_members(session: AsyncSession, team: Team) -> int:
    return await session.scalar(filter_members(select(func.count(TeamMember.id)), team))


async def list_members(session: AsyncSession, offset: int, limit: int, team: Team):
    return await session.scalars(
        filter_members(
            members_options(
                select(TeamMember).offset(offset).limit(limit),
            ),
            team,
        )
    )


# endregion

# region Team Joins


def joins_options(query: Select) -> Select:
    return query.options(
        joinedload(TeamJoinRequest.team),
        joinedload(TeamJoinRequest.user).options(
            joinedload(User.avatar),
            joinedload(User.role),
        ),
    )


async def get_join(session: AsyncSession, team: Team, join_id: int) -> TeamJoinRequest:
    return await session.scalar(
        select(TeamJoinRequest).filter(
            TeamJoinRequest.team_id == team.id, TeamJoinRequest.id == join_id  # type: ignore
        )
    )


def filter_joins(query: Select, team: Team) -> Select:
    return query.filter(
        TeamJoinRequest.team_id == team.id,
    )


async def count_joins(session: AsyncSession, team: Team) -> int:
    return await session.scalar(filter_joins(select(func.count(TeamJoinRequest.id)), team))


async def list_joins(
    session: AsyncSession, offset: int, limit: int, team: Team
) -> ScalarResult[TeamJoinRequest]:
    return await session.scalars(
        filter_joins(
            joins_options(
                select(TeamJoinRequest).offset(offset).limit(limit),
            ),
            team,
        )
    )


async def accept_join(session: AsyncSession, team: Team, join: TeamJoinRequest) -> TeamMember:
    join.status = constants.STATUS_TEAM_JOIN_ACCEPTED

    role = await session.scalar(
        select(Role).filter(Role.name == constants.ROLE_TEAM_MEMBER).limit(1)
    )

    member = TeamMember(
        user=join.user,
        team=team,
        role=role,
    )
    session.add(member)

    await session.commit()

    return member


async def reject_join(session: AsyncSession, join: TeamJoinRequest):
    join.status = constants.STATUS_TEAM_JOIN_REJECTED

    await session.commit()

    return join


# endregion


# region Team members management
async def get_team_member_by_username(
    session: AsyncSession, team: Team, nickname: str
) -> TeamMember:
    return await session.scalar(
        select(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == User.id,
            User.nickname == nickname,
        )
    )


async def kick_team_member(session: AsyncSession, member: TeamMember):
    await session.delete(member)
    await session.commit()

    return member.user


async def update_team_member(session: AsyncSession, member: TeamMember, body: UpdateTeamMemberBody):
    if body.role is not None:
        role = await get_role_by_name(session, body.role)
        member.role = role

    if body.permissions is not None:
        if body.permissions_merge:
            member.local_permissions = merge_permissions(member.local_permissions, body.permissions)
        else:
            member.local_permissions = body.permissions


    if body.pseudonym is not None:
        member.pseudonym = body.pseudonym

    await session.commit()

    return member

# endregion
