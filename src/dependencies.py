from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, Query, Depends, BackgroundTasks, params

from .models import Token
from config import settings
from . import service, scheme, util
from src.database import session_holder, acquire_session

define_error = scheme.define_error_category("token")
token_required = define_error("required", "Token required", 401)
token_expired = define_error("expired", "Token expired", 401)
master_required = define_error("master-required", "Master token required", 401)
permission_denied = scheme.define_error(
    "permissions", "denied", "Permission denied: required permissions: {permissions}", 403
)


async def _use_token(token: str):
    """Update token's ``used_at``, ``expire_at`` and owner's ``next_offline`` columns"""
    async with session_holder.session() as session:
        token = await service.get_token(session, token)

        # Token was deleted in endpoint
        if token is None:
            return

        token.use()
        token.prolong()
        token.owner.prolong_online()
        session.add_all([token, token.owner])
        await session.commit()


@token_expired.mark
async def optional_token(
    background: BackgroundTasks,
    token_body: str | None = Header(
        None,
        alias="Token",
        description="Токен доступу до ресурсу",
        pattern="[a-z0-9]+",
    ),
    session: AsyncSession = Depends(acquire_session),
) -> Token | None:
    """Prevent access to endpoint for users that provide expired token"""
    token = await service.get_token(session, token_body)

    if token is not None and token.expired():
        raise token_expired

    try:
        yield token
    finally:
        # Prolong token, user online status and mark token as used only if it is a real token
        if isinstance(token, Token):
            background.add_task(_use_token, token_body)


@token_required.mark
async def require_token(
    token: Token | None = Depends(optional_token),
):
    """Prevent access to endpoint for users that doesn't provide valid token"""
    if token is None:
        raise token_required

    return token


def master_grant(master_key: str | None = Header(None, description="Master key")) -> bool:
    """Dependency returns true if user passed right master key"""
    return master_key == settings.service.master_key


@master_required.mark
def master_lock(master_granted: bool = Depends(master_grant)):
    """Prevent access to endpoint for users that doesn't provide master key"""
    if not master_granted:
        raise master_required


@lru_cache
def require_permissions(*permissions: str) -> params.Depends:
    """
    Permission shield for endpoint. Filters out all users that doesn't have required permissions.

    Permissions format:
    ::
        CATEGORY = SUBCATEGORY = NAME = [-a-z]+

        PERMISSION = {NAME} | {CATEGORY}.{NAME} | {CATEGORY}.{SUBCATEGORY}.{NAME}

        PERMISSION_ENTRY = "{PERMISSION}" | "{PERMISSION} | {PERMISSION_ENTRY}"

    One permission entry can contain multiple permissions divided by "|".
    In this case if any of permissions in this entry exists in user's permission - this entry will
    pass permission check

    Examples:
    ::
        require_permissions("user.update-info")
        require_permissions("user.own.update-info")
        require_permissions("user.own.update-info | user.update_info")
    """

    @permission_denied.mark
    def dependency(
        master_granted: bool = Depends(master_grant),
        token: Token | None = Depends(optional_token),
    ):
        if master_granted:
            return

        extra = dict(permissions=", ".join(permissions))

        if not isinstance(token, Token):
            raise permission_denied(extra=extra)

        if not util.check_permissions(permissions, token.owner.permissions):
            raise permission_denied(extra=extra)

    setattr(dependency, "permissions", permissions)

    return Depends(dependency)


def require_page(page: int = Query(1, ge=1, description="№ Сторінки")):
    """Return page number provided by user"""
    return page
