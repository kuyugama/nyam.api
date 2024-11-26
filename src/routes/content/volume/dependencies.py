from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import permissions
from .scheme import CreateChapterBody
from src.database import acquire_session
from src.models import Volume, Token, Chapter
from ..composition.variant.dependencies import not_author
from src.service import get_composition_variant, get_next_index, update_next_indexes
from src.dependencies import require_volume, require_token, master_grant, check_permissions


@not_author.mark
async def validate_create_chapter(
    body: CreateChapterBody,
    volume: Volume = Depends(require_volume),
    author_token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
    master_granted: bool = Depends(master_grant),
):
    variant = await get_composition_variant(session, volume.variant_id)

    if variant.author_id != author_token.owner_id and not check_permissions(
        master_granted, author_token, permissions.override_author
    ):
        raise not_author

    if body.index is None:
        body.index = await get_next_index(session, Chapter, Chapter.volume_id == volume.id)
    else:
        await update_next_indexes(session, Chapter, Chapter.volume_id == volume.id, body.index)

    return body
