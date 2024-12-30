from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import scheme, models
from src.routes.teams import service
from src.database import acquire_session
from src.models import Token, Team, User, TeamMember
from src.permissions import permissions, team_permissions
from src.util import Cache, get_offset_and_limit, paginated_response
from .scheme import CreateTeamBody, UpdateTeamBody, TeamJoinRequest, UpdateTeamMemberBody

from .dependencies import (
    require_provided_team_member,
    require_team_permissions,
    require_no_join_request,
    validate_update_member,
    require_team_member,
    require_team_join,
    validate_update,
    require_team,
    validate_kick_member,
)

from src.dependencies import (
    require_permissions,
    require_drop_cache,
    require_cache,
    require_token,
    require_page,
    require_user,
)

router = APIRouter(prefix="/teams", tags=["Команди"])


# region Public team info


@router.get(
    "/",
    summary="Отримати команди",
    response_model=scheme.Paginated[scheme.Team],
    operation_id="list_teams",
)
async def get_teams(
    cache: Cache = require_cache("teams"),
    page: int = Depends(require_page),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    total = await cache((), service.count_teams, session)
    items = await service.list_teams(session, offset=offset, limit=limit)

    return paginated_response(items.all(), total, page, limit)


@router.get(
    "/my",
    summary="Отримати ваші команди",
    response_model=scheme.Paginated[scheme.Team],
    operation_id="list_my_teams",
)
async def get_my_teams(
    cache: Cache = require_cache("teams"),
    page: int = Depends(require_page),
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    total = await cache(("my",), service.count_teams, session, member=token.owner)
    items = await service.list_teams(session, offset=offset, limit=limit, member=token.owner)

    return paginated_response(items.all(), total, page, limit)


@router.get(
    "/{team_id}",
    summary="Отримати команду",
    response_model=scheme.Team,
    operation_id="get_team",
)
async def get_team(
    team: Team = Depends(require_team),
):
    return team


@router.get(
    "/{team_id}/members/",
    summary="Отримати учасників команди",
    response_model=scheme.Paginated[scheme.TeamMember],
    operation_id="list_team_members",
)
async def get_team_members(
    team: Team = Depends(require_team),
    page: int = Depends(require_page),
    cache: Cache = require_cache("teams/members"),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    total = await cache((), service.count_members, session, team)
    items = await service.list_members(session, offset=offset, limit=limit, team=team)

    return paginated_response(items.all(), total, page, limit)


@router.get(
    "/user/{nickname}",
    summary="Отримати команди користувача",
    response_model=scheme.Paginated[scheme.Team],
    operation_id="list_user_teams",
)
async def get_user_teams(
    cache: Cache = require_cache("teams"),
    page: int = Depends(require_page),
    user: User = Depends(require_user),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    total = await cache((), service.count_teams, session, member=user)
    items = await service.list_teams(session, offset=offset, limit=limit, member=user)

    return paginated_response(items.all(), total, page, limit)


# endregion


# region Create, update, inspect owned teams


@router.post(
    "/",
    summary="Створити команду",
    response_model=scheme.Team,
    operation_id="create_team",
    dependencies=[require_drop_cache("teams"), require_permissions(permissions.team.create)],
)
async def create_team(
    body: CreateTeamBody,
    session: AsyncSession = Depends(acquire_session),
    token: Token = Depends(require_token),
):

    return await service.create_team(session, body, token.owner)


@router.patch(
    "/{team_id}",
    summary="Редагувати команду",
    response_model=scheme.Team,
    operation_id="update_team",
    dependencies=[require_team_permissions(team_permissions.team.update)],
)
async def update_team(
    team: Team = Depends(require_team),
    body: UpdateTeamBody = Depends(validate_update),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.update_team(session, team, body)


# endregion


# region Team Joins


@router.post(
    "/{team_id}/joins",
    summary="Створити запит на приєднання в команду",
    response_model=TeamJoinRequest,
    operation_id="join_team",
    dependencies=[Depends(require_no_join_request)],
)
async def join_team(
    team: Team = Depends(require_team),
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.create_join(session, team, token.owner)


@router.get(
    "/{team_id}/joins",
    summary="Отримати запити на участь в команді",
    response_model=scheme.Paginated[TeamJoinRequest],
    operation_id="list_team_join_requests",
    dependencies=[
        require_team_permissions(team_permissions.join.list),
    ],
)
async def list_team_join_requests(
    team: Team = Depends(require_team),
    session: AsyncSession = Depends(acquire_session),
    page: int = Depends(require_page),
    cache: Cache = require_cache("teams/joins"),
):
    offset, limit = get_offset_and_limit(page)

    total = await cache((), service.count_joins, session, team)
    items = await service.list_joins(session, offset=offset, limit=limit, team=team)

    return paginated_response(items.all(), total, page, limit)


@router.post(
    "/{team_id}/joins/{join_id}/accept",
    summary="Схвалити приєднання до команди",
    response_model=scheme.TeamMember,
    operation_id="accept_team_join_request",
    dependencies=[
        require_team_permissions(team_permissions.join.accept),
    ],
)
async def accept_team_join_request(
    team: Team = Depends(require_team),
    join: models.TeamJoinRequest = Depends(require_team_join),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.accept_join(session, team, join)


@router.post(
    "/{team_id}/joins/{join_id}/reject",
    summary="Відхилити запит на приєднання в команду",
    response_model=TeamJoinRequest,
    operation_id="reject_team_join_request",
    dependencies=[
        require_team_permissions(team_permissions.join.reject),
    ],
)
async def reject_team_join_request(
    join: models.TeamJoinRequest = Depends(require_team_join),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.reject_join(session, join)


# endregion


# region Team Members management


@router.delete(
    "/{team_id}/members/{nickname}",
    summary="Вигнати учасника команди",
    response_model=scheme.User,
    operation_id="kick_team_member",
    dependencies=[
        require_team_permissions(team_permissions.member.kick),
        Depends(validate_kick_member),
    ],
)
async def kick_team_member(
    member: TeamMember = Depends(require_provided_team_member),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.kick_team_member(session, member)


@router.patch(
    "/{team_id}/members/{nickname}",
    summary="Редагувати учасника команди: встановити псевдонім, роль, права",
    response_model=scheme.TeamMember,
    operation_id="update_team_member",
    dependencies=[
        require_team_permissions(team_permissions.team.update),
    ],
)
async def update_team_member(
    body: UpdateTeamMemberBody = Depends(validate_update_member),
    member: TeamMember = Depends(require_provided_team_member),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.update_team_member(session, member, body)


@router.post(
    "/{team_id}/leave",
    summary="Покинути команду",
    response_model=scheme.TeamMember,
    operation_id="leave_team",
)
async def leave_team(
    member: TeamMember = Depends(require_team_member),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.kick_team_member(session, member)


# endregion


# region Team management by privileged users


@router.post(
    "/{team_id}/verify",
    summary="Верифікувати команду",
    response_model=scheme.Team,
    operation_id="verify_team",
    dependencies=[
        require_permissions(permissions.team.verify),
    ],
)
async def verify_team(
    team: Team = Depends(require_team),
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.verify_team(session, team, token.owner)


@router.delete(
    "/{team_id}/verify",
    summary="Зняти верифікацію з команди",
    response_model=scheme.Team,
    operation_id="unverify_team",
    dependencies=[
        require_permissions(permissions.team.verify),
    ],
)
async def unverify_team(
    team: Team = Depends(require_team),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.unverify_team(session, team)


# endregion
