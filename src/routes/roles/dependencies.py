from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src.models import Role
from src import scheme, util
from src.service import get_lowest_role
from src.database import acquire_session
from .scheme import CreateRoleBody, UpdateRoleBody

define_error = scheme.define_error_category("roles")
name_occupied = define_error("name-occupied", "Role name occupied", 400)
weight_required = define_error("weight-required", "Role weight or base role must be specified", 400)
default_role_already_exist = define_error(
    "default-role-already-exist", "Default role already exist", 400
)
role_not_exist = define_error("role-not-exist", "Role not exist", 404)
role_has_users = define_error(
    "role-has-users",
    "Role has users. To delete role you must set replacement parameter",
    400,
)
replacement_role_not_exist = define_error(
    "replacement-role-not-exist", "Replacement role not exist", 404
)
base_role_not_exist = define_error("base-role-not-exist", "Base role not exist", 404)


@name_occupied.mark()
@weight_required.mark()
@base_role_not_exist.mark()
@default_role_already_exist.mark()
async def validate_role_create(
    body: CreateRoleBody, session: AsyncSession = Depends(acquire_session)
) -> CreateRoleBody:
    role = await service.get_role_by_name(session, body.name)
    if role is not None:
        raise name_occupied

    if body.default and await get_lowest_role(session):
        raise default_role_already_exist

    if body.base_role is not None:
        base_role = await service.get_role_by_name(session, body.base_role)
        if base_role is None:
            raise base_role_not_exist

        body.weight = body.weight or base_role.weight
        body.permissions = base_role.permissions | body.permissions

    if body.weight is None:
        raise weight_required

    return body


@role_not_exist.mark()
async def validate_role(name: str, session: AsyncSession = Depends(acquire_session)) -> Role:
    role = await service.get_role_by_name(session, name)
    if role is None:
        raise role_not_exist

    return role


@default_role_already_exist.mark()
async def validate_role_update(
    body: UpdateRoleBody,
    session: AsyncSession = Depends(acquire_session),
):
    if body.default and await get_lowest_role(session):
        raise default_role_already_exist

    return body


@util.has_errors(replacement_role_not_exist, role_has_users, role_not_exist)
async def validate_role_delete(
    name: str,
    replacement: str | None = Query(None, description="Replacement role"),
    session: AsyncSession = Depends(acquire_session),
):
    role = await service.get_role_by_name(session, name)

    if role is None:
        raise role_not_exist

    # Fallback to default role if replacement not set
    if replacement is None:
        fallback_role = await get_lowest_role(session)
        if fallback_role is not None and fallback_role.name != name:
            return role, fallback_role

    if replacement is not None:
        replacement_role = await service.get_role_by_name(session, replacement)

        if replacement_role is None or role == replacement_role:
            raise replacement_role_not_exist

        return role, replacement_role

    if await service.has_users(session, name):
        raise role_has_users

    return role, None
