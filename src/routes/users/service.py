import mimetypes
import secrets

from PIL import Image
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from src import constants, util
from src.scheme.error import APIError
from src.models import User, UploadImage, Role
from .scheme import UpdateUserBody, UpdateOtherUserBody

from src.util import (
    filter_image_size,
    upload_file_obj,
    compress_png,
    delete_obj,
)


async def update_user(
    session: AsyncSession,
    user: User,
    body: UpdateUserBody | UpdateOtherUserBody,
) -> User:
    if body.nickname is not None:
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
                constants.MAX_AVATAR_WIDTH,
                constants.MAX_AVATAR_HEIGHT,
            )
            mime = "image/webp"
        else:
            file = filter_image_size(
                upload_file.file,
                constants.MAX_AVATAR_WIDTH,
                constants.MAX_AVATAR_HEIGHT,
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

    key = "{nickname}/avatar-{hex}{ext}".format(
        nickname=user.nickname,
        hex=secrets.token_hex(8),
        ext=mimetypes.guess_extension(mime),
    )

    await upload_file_obj(file, key, mime)

    avatar = UploadImage(
        url=settings.cdn.url_format.format(
            key=key,
        ),
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
