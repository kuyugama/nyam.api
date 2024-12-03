from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.scheme import APIError
from src.util import has_errors
from src import constants, scheme
from src.models import Token, User
from src.permissions import permissions
from src.database import acquire_session
from src.service import get_role_by_name, get_user_by_nickname
from src.routes.users.scheme import UpdateUserBody, UpdateOtherUserBody

from src.dependencies import (
    file_mime,
    master_grant,
    require_token,
    optional_token,
    require_permissions,
)

define_error = scheme.define_error_category("users")
role_not_found = define_error(
    "role-not-found",
    "Role not found",
    404,
)
user_not_found = define_error(
    "not-found",
    "User with that nickname not found",
    404,
)
empty_update = define_error(
    "empty-update",
    "Empty update body",
    400,
)
nothing_to_update = define_error(
    "nothing-to-update",
    "Nothing to update",
    400,
)
invalid_avatar_mime = define_error(
    "invalid-avatar-mime",
    "Invalid avatar file type",
    400,
)
avatar_too_big = define_error(
    "avatar-too-big",
    "Avatar file too big",
    400,
)


@has_errors(empty_update, nothing_to_update)
async def validate_update_user(
    body: UpdateUserBody,
    token: Token | User = Depends(require_token),
):
    if isinstance(token, User):
        user = token
    else:
        user = token.owner

    if not (
        body.nickname
        or body.pseudonym
        or body.remove_pseudonym
        or body.description
        or body.remove_description
        or body.remove_avatar
        or isinstance(body, UpdateOtherUserBody)
        and body.permissions
    ):
        raise empty_update

    if body.remove_pseudonym and user.pseudonym is None:
        body.remove_pseudonym = False

    if body.remove_description and user.description is None:
        body.remove_description = False

    if (
        (body.nickname is None or body.nickname == user.nickname)
        and (body.pseudonym == user.pseudonym and not body.remove_pseudonym)
        and (body.description == user.description and not body.remove_description)
    ):
        raise nothing_to_update

    return body


@has_errors(invalid_avatar_mime, avatar_too_big)
def validate_avatar(
    file: UploadFile,
    mime: str = Depends(file_mime),
):
    if mime not in constants.AVATAR_ALLOWED_MIMES:
        raise invalid_avatar_mime

    if file.size > constants.AVATAR_MAX_SIZE:
        raise avatar_too_big

    return file.file


@role_not_found.mark
async def validate_role(role_name: str, session: AsyncSession = Depends(acquire_session)):
    role = await get_role_by_name(session, role_name)
    if not role:
        raise role_not_found

    return role


@user_not_found.mark
async def validate_user(nickname: str, session: AsyncSession = Depends(acquire_session)):
    user = await get_user_by_nickname(session, nickname)
    if not user:
        raise user_not_found

    return user


@has_errors(empty_update, nothing_to_update)
async def validate_update_other_user(
    body: UpdateOtherUserBody,
    user: User = Depends(validate_user),
    token: Token = Depends(optional_token),
    master_granted: bool = Depends(master_grant),
):
    permission_validator = require_permissions(permissions.user.permission_management).dependency

    body.permissions is not None and permission_validator(master_granted, token)

    try:
        await validate_update_user(body, user)
    except APIError as e:
        if e.code not in (nothing_to_update.code, empty_update.code):
            raise

        # If permissions are empty - re-raise
        if body.permissions is None:
            raise

    if body.permissions == user.local_permissions:
        raise nothing_to_update

    return body
