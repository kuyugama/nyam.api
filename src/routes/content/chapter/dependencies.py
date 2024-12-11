from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Query, File, UploadFile

from . import service
from src import constants
from .scheme import PublishTextPageBody
from src.database import acquire_session
from src.scheme import define_error_category
from src.permissions import team_permissions
from src.util import requires_permissions, check_permissions
from src.service import get_next_index, update_next_indexes, get_team_member
from src.models import Chapter, Token, CompositionVariant, BasePage, TeamMember

from src.dependencies import (
    file_mime,
    master_grant,
    require_token,
    require_chapter,
    permission_denied,
)

define_error = define_error_category("content/page")
image_too_big = define_error("image-too-big", "Page image too big", 400)
mime_invalid = define_error("mime-invalid", "Invalid page image file type", 400)
type_invalid = define_error("type-invalid", "Invalid page type", 400)

teams = define_error_category("teams")
not_member = teams("not-member", "You're not a member of the team", 403)


_text_page_required_permissions = (team_permissions.page.text.create,)
_image_page_required_permissions = (team_permissions.page.image.create,)


async def chapter_composition_variant(
    chapter: Chapter = Depends(require_chapter),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.get_composition_variant(session, chapter.id)


@not_member.mark
async def require_team_member(
    chapter: Chapter = Depends(require_chapter),
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    team_member = await get_team_member(session, chapter.team_id, token.owner_id)

    if team_member is None:
        raise not_member

    return team_member


@type_invalid.mark
@permission_denied.mark
@requires_permissions(_text_page_required_permissions)
async def validate_publish_text_page(
    body: PublishTextPageBody,
    chapter: Chapter = Depends(require_chapter),
    session: AsyncSession = Depends(acquire_session),
    variant: CompositionVariant = Depends(chapter_composition_variant),
    team_member: TeamMember = Depends(require_team_member),
    master_granted: bool = Depends(master_grant),
):
    if (
        not check_permissions(_text_page_required_permissions, team_member.permissions)
        and not master_granted
    ):
        raise permission_denied(
            extra=dict(permissions=", ".join(map(str, _text_page_required_permissions)))
        )

    if constants.COMPOSITION_STYLE_TO_PAGE_TYPE[variant.origin.style] != constants.PAGE_TEXT:
        raise type_invalid

    if body.index is None:
        body.index = await get_next_index(session, BasePage, BasePage.chapter_id == chapter.id)
    else:
        await update_next_indexes(session, BasePage, BasePage.chapter_id == chapter.id, body.index)

    return body


@permission_denied.mark
@requires_permissions(_image_page_required_permissions)
async def validate_image_page_permissions(
    team_member: TeamMember = Depends(require_team_member),
    master_granted: bool = Depends(master_grant),
):
    if (
        not check_permissions(_image_page_required_permissions, team_member.permissions)
        and not master_granted
    ):
        raise permission_denied(
            extra=dict(permissions=", ".join(map(str, _image_page_required_permissions)))
        )


async def validate_image_page_index(
    index: int | None = Query(
        None,
        description="Порядковий номер сторінки, необов'язкове значення, "
        "якщо не вказано створиться автоматично",
    ),
    chapter: Chapter = Depends(require_chapter),
    session: AsyncSession = Depends(acquire_session),
):

    if index is None:
        index = await get_next_index(session, BasePage, BasePage.chapter_id == chapter.id)
    else:
        await update_next_indexes(session, BasePage, BasePage.chapter_id == chapter.id, index)

    return index


@image_too_big.mark
@mime_invalid.mark
@type_invalid.mark
async def validate_image_page_file(
    file: UploadFile = File(description="Зображення сторінки"),
    mime: str = Depends(file_mime),
    variant: CompositionVariant = Depends(chapter_composition_variant),
):
    if constants.COMPOSITION_STYLE_TO_PAGE_TYPE[variant.origin.style] != constants.PAGE_IMAGE:
        raise type_invalid

    if file.size > constants.PAGE_MAX_SIZE:
        raise image_too_big

    if mime not in constants.PAGE_ALLOWED_MIMES:
        raise mime_invalid

    return file
