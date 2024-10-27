import puremagic
from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Token
from src.scheme import APIError
from src.util import has_errors
from src.database import acquire_session
from src import constants, scheme, permissions
from src.service import get_role_by_name, get_user_by_nickname
from src.dependencies import require_token, require_permissions, master_grant
from src.routes.users.scheme import UpdateUserBody, UpdateOtherUserBody

MB = 1024 * 1024

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
    token: Token = Depends(require_token),
):
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

    if body.remove_pseudonym and token.owner.pseudonym is None:
        body.remove_pseudonym = False

    if body.remove_description and token.owner.description is None:
        body.remove_description = False

    if (
        (body.nickname is None or body.nickname == token.owner.nickname)
        and (body.pseudonym == token.owner.pseudonym and not body.remove_pseudonym)
        and (body.description == token.owner.description and not body.remove_description)
    ):
        raise nothing_to_update

    return body


@has_errors(empty_update, nothing_to_update)
async def validate_update_other_user(
    body: UpdateOtherUserBody,
    token: Token = Depends(require_token),
    master_granted: bool = Depends(master_grant),
):
    permission_validator = require_permissions(permissions.user.permission_management).dependency

    body.permissions is not None and permission_validator(master_granted, token)

    try:
        await validate_update_user(body, token)
    except APIError as e:
        if e.code not in (nothing_to_update.code, empty_update.code):
            raise

        # If permissions are empty - re-raise
        if body.permissions is None:
            raise

    if body.permissions == token.owner.local_permissions:
        raise nothing_to_update

    return body


def file_mime(file: UploadFile) -> str:
    return puremagic.from_stream(file.file, True, file.filename)


@has_errors(invalid_avatar_mime, avatar_too_big)
def validate_avatar(
    file: UploadFile,
    mime: str = Depends(file_mime),
):
    if mime not in ("image/png", "image/jpeg", "image/webp"):
        raise invalid_avatar_mime

    if file.size > constants.MAX_AVATAR_SIZE:
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
