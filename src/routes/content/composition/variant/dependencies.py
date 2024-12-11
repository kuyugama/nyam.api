from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .scheme import CreateVolumeBody
from src.database import acquire_session
from src.scheme import define_error_category
from src.permissions import team_permissions
from src.util import check_permissions, requires_permissions
from src.models import CompositionVariant, Token, Volume, TeamMember
from src.dependencies import require_composition_variant, permission_denied
from src.service import get_next_index, update_next_indexes, get_team_member

from src.dependencies import (
    master_grant,
    require_token,
)

define_error = define_error_category("teams")
not_member = define_error("not-member", "You're not a member of the team", 403)

_required_permissions = (team_permissions.volume.create,)


@not_member.mark
async def require_team_member(
    variant: CompositionVariant = Depends(require_composition_variant),
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    team_member = await get_team_member(session, variant.team_id, token.owner_id)

    if team_member is None:
        raise not_member

    return team_member


@not_member.mark
@permission_denied.mark
@requires_permissions(_required_permissions)
async def validate_create_volume(
    body: CreateVolumeBody,
    variant: CompositionVariant = Depends(require_composition_variant),
    team_member: TeamMember = Depends(require_team_member),
    session: AsyncSession = Depends(acquire_session),
    master_granted: bool = Depends(master_grant),
):
    if not check_permissions(_required_permissions, team_member.permissions) and not master_granted:
        raise permission_denied(
            extra=dict(permissions=", ".join(map(str, _required_permissions))),
        )

    if body.index is None:
        body.index = await get_next_index(session, Volume, Volume.variant_id == variant.id)
    else:
        await update_next_indexes(session, Volume, Volume.variant_id == variant.id, body.index)

    return body
