import secrets
import mimetypes

from PIL import Image
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from src import constants, util
from src.scheme.error import APIError
from src.models import User, UploadImage, Role
from .scheme import UpdateUserBody, UpdateOtherUserBody

from src.util import (
    delete_obj,
    compress_png,
    upload_file_obj,
    filter_image_size,
)


async def update_user(
    session: AsyncSession,
    user: User,
    body: UpdateUserBody | UpdateOtherUserBody,
    updated_by: User | None = None,
) -> User:
    from tasks import user_nickname_updated

    if body.nickname is not None:
        user_nickname_updated.send(
            user.id, user.nickname, body.nickname, updated_by and updated_by.id
        )
        user.nickname = body.nickname

    if body.pseudonym is not None:
        user.pseudonym = body.pseudonym

    if body.remove_pseudonym:
        user.pseudonym = None

    if body.description is not None:
        user.description = body.description

    if body.remove_description:
        user.description = None

    if body.remove_avatar and user.avatar:
        avatar = user.avatar
        user.avatar = None
        await util.delete_obj(avatar.key)
        await session.delete(avatar)

    if isinstance(body, UpdateOtherUserBody) and body.permissions:
        if body.merge_permissions:
            user.local_permissions.update(body.permissions)
        else:
            user.local_permissions = body.permissions

    await session.commit()

    return user


async def update_user_avatar(
    session: AsyncSession, user: User, upload_file: UploadFile, mime: str
) -> User:
    try:
        if mime == "image/png":
            file = compress_png(
                upload_file.file,
                constants.AVATAR_MAX_WIDTH,
                constants.AVATAR_MAX_HEIGHT,
            )
            mime = "image/webp"
        else:
            file = filter_image_size(
                upload_file.file,
                constants.AVATAR_MAX_WIDTH,
                constants.AVATAR_MAX_HEIGHT,
            )

        width, height = Image.open(file).size
        file.seek(0)
    except Exception as e:
        raise APIError("users", "image-handling-error", extra={"message": e.args[0]})

    if user.avatar:
        avatar = user.avatar
        user.avatar = None

        # If avatar saved at our cdn - delete it
        if avatar.key:
            await delete_obj(avatar.key)

        await session.delete(avatar)

    key = settings.cdn.key_format.avatar.format(
        nickname=user.nickname,
        hex=secrets.token_hex(8),
        ext=mimetypes.guess_extension(mime),
    )

    await upload_file_obj(file, key, mime)

    avatar = UploadImage(
        url=settings.cdn.url_format.format(key=key),
        width=width,
        height=height,
        mime_type=mime,
        key=key,
    )

    session.add(avatar)

    user.avatar = avatar

    await session.commit()

    return user


async def update_user_role(session: AsyncSession, user: User, role: Role) -> User:
    user.role = role

    await session.commit()

    return user
