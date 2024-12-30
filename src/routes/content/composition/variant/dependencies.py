from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .scheme import CreateVolumeBody
from src.database import acquire_session
from src.models import CompositionVariant, Volume
from src.dependencies import require_composition_variant
from src.service import get_next_index, update_next_indexes


async def require_team_id(
    variant: CompositionVariant = Depends(require_composition_variant),
) -> int:
    return variant.team_id


async def validate_create_volume(
    body: CreateVolumeBody,
    variant: CompositionVariant = Depends(require_composition_variant),
    session: AsyncSession = Depends(acquire_session),
):
    if body.index is None:
        body.index = await get_next_index(session, Volume, Volume.variant_id == variant.id)
    else:
        await update_next_indexes(session, Volume, Volume.variant_id == variant.id, body.index)

    return body
