from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import permissions
from .scheme import CreateVolumeBody
from src.database import acquire_session
from src.scheme import define_error_category
from src.dependencies import require_composition_variant
from src.models import CompositionVariant, Token, Volume
from src.service import get_next_index, update_next_indexes

from src.dependencies import (
    master_grant,
    require_token,
    check_permissions,
)

define_error = define_error_category("content/composition/variant")
not_author = define_error("not-author", "You're not a composition variant author", 403)


@not_author.mark
async def validate_create_volume(
    body: CreateVolumeBody,
    variant: CompositionVariant = Depends(require_composition_variant),
    author_token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
    master_granted: bool = Depends(master_grant),
):
    if variant.author_id != author_token.owner_id and not check_permissions(
        master_granted, author_token, permissions.override_author
    ):
        raise not_author

    if body.index is None:
        body.index = await get_next_index(session, Volume, Volume.variant_id == variant.id)
    else:
        await update_next_indexes(session, Volume, Volume.variant_id == variant.id, body.index)

    return body
