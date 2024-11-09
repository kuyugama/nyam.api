import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import util
from src.models import Role
from src.routes.roles import service
from src.database import acquire_session
from src.dependencies import require_page, master_lock
from .scheme import CreateRoleBody, UpdateRoleBody, FullRole, Paginated

from .dependencies import (
    validate_role,
    validate_role_create,
    validate_role_update,
    validate_role_delete,
)

router = fastapi.APIRouter(prefix="/roles", tags=["Ролі"])


@router.get("", response_model=Paginated[FullRole], operation_id="get_roles")
async def get_roles(
    page: int = Depends(require_page),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = util.get_offset_and_limit(page)

    total = await service.count_roles(session)
    items = await service.list_roles(session, offset=offset, limit=limit)

    return util.paginated_response(items.all(), total, page, limit)


@router.post(
    "/",
    response_model=FullRole,
    dependencies=[Depends(master_lock)],
    operation_id="create_role",
)
async def create_role(
    body: CreateRoleBody = Depends(validate_role_create),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.create_role(session, body)


@router.patch(
    "/{name}",
    response_model=FullRole,
    dependencies=[Depends(master_lock)],
    operation_id="update_role",
)
async def update_role(
    role: Role = Depends(validate_role),
    body: UpdateRoleBody = Depends(validate_role_update),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.update_role(session, body, role)


@router.delete(
    "/{name}",
    response_model=FullRole,
    dependencies=[Depends(master_lock)],
    operation_id="delete_role",
)
async def delete_role(
    roles: tuple[Role, Role | None] = Depends(validate_role_delete),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.delete_role(session, *roles)
