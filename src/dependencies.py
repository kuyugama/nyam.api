import warnings
from functools import lru_cache

import puremagic
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, Query, Depends, BackgroundTasks, params, Request, UploadFile, FastAPI

from config import settings
from .util import cache_key_hash
from . import service, scheme, util
from src.database import session_holder, acquire_session
from .models import Token, CompositionVariant, Volume, Chapter

define_error = scheme.define_error_category("token")
token_required = define_error("required", "Token required", 401)
token_expired = define_error("expired", "Token expired", 401)
master_required = define_error("master-required", "Master token required", 401)
permission_denied = scheme.define_error(
    "permissions", "denied", "Permission denied: required permissions: {permissions}", 403
)


def client_details(request: Request) -> scheme.ClientInfo:
    agent = request.headers.get("User-Agent", None)

    if request.client:
        return scheme.ClientInfo(request.client.host, agent)

    if "x-forwarder-for" in request.headers:
        return scheme.ClientInfo(request.headers["x-forwarder-for"], agent)

    if "x-real-ip" in request.headers:
        return scheme.ClientInfo(request.headers["x-real-ip"], agent)


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


async def _drop_expired_tokens():
    async with session_holder.session() as session:
        await service.drop_expired_tokens(session)


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

        background.add_task(_drop_expired_tokens)


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


def check_permissions(master_granted: bool, token: Token | None, *permissions: str) -> bool:
    if master_granted:
        return True

    if not isinstance(token, Token):
        return False

    if not util.check_permissions(permissions, token.owner.permissions):
        return False

    return True


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
        if not check_permissions(master_granted, token, *permissions):
            raise permission_denied(extra=dict(permissions=", ".join(permissions)))

    setattr(dependency, "permissions", permissions)

    return Depends(dependency)


@permission_denied.mark
@lru_cache
def interactive_require_permissions(
    master_granted: bool = Depends(master_grant), token: Token | None = Depends(optional_token)
):
    """
    Interactive permission shield for endpoint. Filters out all users that doesn't have required permissions.

    Permissions format:
    ::
        CATEGORY = SUBCATEGORY = NAME = [-a-z]+

        PERMISSION = {NAME} | {CATEGORY}.{NAME} | {CATEGORY}.{SUBCATEGORY}.{NAME}

        PERMISSION_ENTRY = "{PERMISSION}" | "{PERMISSION} | {PERMISSION_ENTRY}"

    One permission entry can contain multiple permissions divided by "|".
    In this case if any of permissions in this entry exists in user's permission - this entry will
    pass permission check

    Example:
    ::
        async def dependency(check_permission = interactive_require_permissions):
            content = await service.get_content(...)
            check_permission(permissions.content[content.type].update)
    """

    def permission_checker(*permissions: str) -> bool:
        if not check_permissions(master_granted, token, *permissions):
            raise permission_denied(extra=dict(permissions=", ".join(permissions)))

        return True

    return Depends(permission_checker)


def require_page(page: int = Query(1, ge=1, description="№ Сторінки")):
    """Return page number provided by user"""
    return page


not_found = scheme.define_error(
    "content/composition/variant", "not-found", "Composition variant not found", 404
)


@not_found.mark
async def require_composition_variant(
    variant_id: int, session: AsyncSession = Depends(acquire_session)
) -> CompositionVariant:
    variant = await service.get_composition_variant(session, variant_id)
    if variant is None:
        raise not_found

    return variant


not_found = scheme.define_error("content/volume", "not-found", "Volume not found", 404)


@not_found.mark
async def require_volume(
    volume_id: int, session: AsyncSession = Depends(acquire_session)
) -> Volume:
    volume = await service.get_volume(session, volume_id)
    if volume is None:
        raise not_found

    return volume


not_found = scheme.define_error("content/chapter", "not-found", "Chapter not found", 404)


@not_found.mark
async def require_chapter(
    chapter_id: int, session: AsyncSession = Depends(acquire_session)
) -> Chapter:
    chapter = await service.get_chapter(session, chapter_id)
    if chapter is None:
        raise not_found

    return chapter


def file_mime(file: UploadFile) -> str:
    return puremagic.from_stream(file.file, True, file.filename)


@lru_cache
def require_use_cache(key: str):
    """
    Dependency generates function to save result of coroutines using cache key

    :param key: cache context key (can be used to drop cache)
    :return: (tuple<Any, ...>, Awaitable<T>) -> Awaitable<T>
    """

    def dependency(request: Request):
        # Ignore not awaited coroutines
        warnings.simplefilter("ignore", RuntimeWarning)

        app: FastAPI = request.scope["app"]

        if not hasattr(app, "user_cache"):
            app.user_cache = {}

        cache = app.user_cache.setdefault(key, {})

        async def use_cache(cache_key, coro):
            nonlocal cache
            key = cache_key_hash(cache_key)

            if key in cache:
                return cache[key]

            return cache.setdefault(key, await coro)

        yield use_cache

    return Depends(dependency)


@lru_cache
def require_drop_cache(key: str):
    """
    Drop all cache at specified key
    """

    def dependency(request: Request):
        app: FastAPI = request.scope["app"]
        if not hasattr(app, "user_cache"):
            app.user_cache = {}

        cache = app.user_cache.setdefault(key, {})

        async def drop_cache():
            cache.clear()

        yield drop_cache

        if cache:
            cache.clear()

    return Depends(dependency)
