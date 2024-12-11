from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .scheme import CreateChapterBody
from src.database import acquire_session
from src.permissions import team_permissions
from src.scheme import define_error_category
from src.models import Volume, Token, Chapter, TeamMember
from src.util import check_permissions, requires_permissions
from src.service import get_next_index, update_next_indexes, get_team_member
from src.dependencies import require_volume, require_token, master_grant, permission_denied

define_error = define_error_category("teams")
not_member = define_error("not-member", "You're not a member of the team", 403)


_required_permissions = (team_permissions.chapter.create,)


@not_member.mark
async def require_team_member(
    volume: Volume = Depends(require_volume),
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    team_member = await get_team_member(session, volume.team_id, token.owner_id)
    if not team_member:
        raise not_member

    return team_member


@permission_denied.mark
@requires_permissions(_required_permissions)
async def validate_create_chapter(
    body: CreateChapterBody,
    volume: Volume = Depends(require_volume),
    session: AsyncSession = Depends(acquire_session),
    master_granted: bool = Depends(master_grant),
    team_member: TeamMember = Depends(require_team_member),
):

    if not check_permissions(_required_permissions, team_member.permissions) and not master_granted:
        raise permission_denied(
            extra=dict(permissions=", ".join(map(str, _required_permissions))),
        )

    if body.index is None:
        body.index = await get_next_index(session, Chapter, Chapter.volume_id == volume.id)
    else:
        await update_next_indexes(session, Chapter, Chapter.volume_id == volume.id, body.index)

    return body
