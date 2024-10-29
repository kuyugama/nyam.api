from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src import scheme
from src import permissions
from src.routes.users import service
from src.models import Token, User, Role
from src.database import acquire_session
from .scheme import UpdateUserBody, UpdateOtherUserBody
from src.dependencies import require_token, require_permissions, optional_token

from .dependencies import (
    file_mime,
    validate_role,
    validate_user,
    validate_avatar,
    validate_update_user,
    validate_update_other_user,
)

router = APIRouter(prefix="/users", tags=["Користувачі"])


@router.get(
    "/me",
    response_model=scheme.FullUser,
    summary="Отримати інформацію про власника токена",
    operation_id="get_me",
)
async def me(token: Token = Depends(require_token)):
    return token.owner


@router.patch(
    "/me",
    response_model=scheme.FullUser,
    summary="Змінити інформацію про власника токену",
    operation_id="update_own_info",
    dependencies=[require_permissions(permissions.user.own.update_info)],
)
async def update_me(
    body: UpdateUserBody = Depends(validate_update_user),
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.update_user(session, token.owner, body, token.owner)


@router.post(
    "/me/avatar",
    response_model=scheme.FullUser,
    summary="Змінити аватар власника токену",
    operation_id="update_own_avatar",
    dependencies=[require_permissions(permissions.user.own.update_info)],
)
async def update_me_avatar(
    file: UploadFile = Depends(validate_avatar),
    mime: str = Depends(file_mime),
    session: AsyncSession = Depends(acquire_session),
    token: Token = Depends(require_token),
):
    """
    Майте на увазі, що зображення будуть стиснуті до 1024x1024 (Стискатиметься лише та сторона,
    яка більше за 1024 пікселі, або обидві). Також, якщо подано зображення у форматі PNG - воно
    буде переформатовано у WEBP
    """
    return await service.update_user_avatar(session, token.owner, file, mime)


@router.get(
    "/{nickname}",
    response_model=scheme.User,
    summary="Отримати інформацію про користувача",
    operation_id="get_user_by_nickname",
)
async def get_user(user: User = Depends(validate_user)) -> scheme.User:
    return user


@router.post(
    "/{nickname}/role/{role_name}",
    response_model=scheme.User,
    summary="Змінити роль користувача",
    operation_id="update_user_role",
    dependencies=[require_permissions(permissions.user.role_management)],
)
async def update_user_role(
    user: User = Depends(validate_user),
    role: Role = Depends(validate_role),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.update_user_role(session, user, role)


@router.patch(
    "/{nickname}",
    response_model=scheme.User,
    summary="Змінити дані користувача",
    operation_id="update_user_info",
    dependencies=[require_permissions(permissions.user.update_info)],
)
async def update_user_info(
    body: UpdateOtherUserBody = Depends(validate_update_other_user),
    user: User = Depends(validate_user),
    token: Token | None = Depends(optional_token),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.update_user(session, user, body, token and token.owner)


@router.post(
    "/{nickname}/avatar",
    response_model=scheme.User,
    summary="Змінити аватар користувача",
    operation_id="update_user_avatar",
    dependencies=[require_permissions(permissions.user.update_info)],
)
async def update_user_avatar(
    file: UploadFile = Depends(validate_avatar),
    mime: str = Depends(file_mime),
    user: User = Depends(validate_user),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.update_user_avatar(session, user, file, mime)
