from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, ScalarResult, update

from src.models import Role, User
from src.service import get_role_by_name
from src.routes.roles.scheme import CreateRoleBody, UpdateRoleBody


__all__ = [
    "has_users",
    "list_roles",
    "create_role",
    "update_role",
    "count_roles",
    "delete_role",
    "get_role_by_name",
]


async def has_users(session: AsyncSession, name: str) -> bool:
    return not not await session.scalar(
        select(func.count(User.id))
        .filter(
            User.role_id == Role.id,  # type: ignore
            Role.name == name,
        )
        .limit(1)
    )


async def create_role(session: AsyncSession, body: CreateRoleBody) -> Role | None:
    role = Role(
        name=body.name,
        title=body.title,
        weight=body.weight,
        default=body.default,
        permissions=body.permissions,
    )
    session.add(role)
    await session.commit()

    return role


async def count_roles(session: AsyncSession):
    return await session.scalar(select(func.count(Role.id)))


async def list_roles(session: AsyncSession, offset: int, limit: int) -> ScalarResult[Role]:
    return await session.scalars(
        select(Role)
        .order_by(Role.updated_at.desc(), Role.created_at.desc())
        .offset(offset)
        .limit(limit)
    )


async def update_role(session: AsyncSession, body: UpdateRoleBody, role: Role):
    if body.title is not None:
        role.title = body.title

    if body.default is not None:
        role.default = body.default

    if body.permissions is not None:
        if body.merge_permissions:
            role.permissions.update(body.permissions)
        else:
            role.permissions = body.permissions

    if body.weight is not None:
        role.weight = body.weight

    await session.commit()

    return role


async def delete_role(session: AsyncSession, role: Role, replacement_role: Role):
    if replacement_role is not None:
        await session.execute(
            update(User).values(role_id=replacement_role.id).filter_by(role_id=role.id)
        )

    await session.delete(role)
    await session.commit()
    return role
