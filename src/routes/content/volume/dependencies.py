from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .scheme import CreateChapterBody
from src.models import Volume, Chapter
from src.database import acquire_session
from src.dependencies import require_volume
from src.service import get_next_index, update_next_indexes


def require_team_id(
    volume: Volume = Depends(require_volume),
) -> int:
    return volume.team_id


async def validate_create_chapter(
    body: CreateChapterBody,
    volume: Volume = Depends(require_volume),
    session: AsyncSession = Depends(acquire_session),
):

    if body.index is None:
        body.index = await get_next_index(session, Chapter, Chapter.volume_id == volume.id)
    else:
        await update_next_indexes(session, Chapter, Chapter.volume_id == volume.id, body.index)

    return body
