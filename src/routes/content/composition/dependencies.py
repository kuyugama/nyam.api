from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src.service import get_team_member
from src.database import acquire_session
from src.models import Composition, Token
from ..dependencies import require_provider
from src.permissions import team_permissions
from .scheme import CreateCompositionVariantBody
from src.content_providers import BaseContentProvider
from src.util import check_permissions, requires_permissions
from src.dependencies import require_token, permission_denied
from src.scheme import define_error_category, define_error as define_error_schema

define_error = define_error_category("content/composition")
provider_composition_not_found = define_error(
    "provider-composition-not-found", "Provider composition not found", 404
)
composition_already_exists = define_error("already-exists", "Composition already exists", 400)
composition_not_found = define_error("not-found", "Composition not found", 404)
not_member = define_error_schema("teams", "not-member", "You're not a member of the team", 403)

_required_permissions_to_create_variant = (team_permissions.content_variant.create,)


@provider_composition_not_found.mark
@composition_already_exists.mark
async def require_provider_composition(
    provider_id: str,
    provider: BaseContentProvider = Depends(require_provider),
    session: AsyncSession = Depends(acquire_session),
):
    provider_composition = await provider.parse_composition(provider_id)

    if provider_composition is None:
        raise provider_composition_not_found

    if await service.get_composition_by_slug(session, provider_composition.slug) is not None:
        raise composition_already_exists

    return provider_composition


@composition_not_found.mark
async def require_composition(
    slug: str,
    session: AsyncSession = Depends(acquire_session),
) -> Composition:
    composition = await service.get_composition_by_slug(session, slug)
    if composition is None:
        raise composition_not_found

    return composition


async def require_team_member(
    body: CreateCompositionVariantBody,
    token: Token = Depends(require_token),
    session: AsyncSession = Depends(acquire_session),
):
    team_member = await get_team_member(session, body.team_id, token.owner_id)

    if team_member is None:
        raise not_member

    return team_member


@permission_denied.mark
@requires_permissions(_required_permissions_to_create_variant)
async def validate_create_variant(
    body: CreateCompositionVariantBody,
    team_member=Depends(require_team_member),
):
    if not check_permissions(_required_permissions_to_create_variant, team_member.permissions):
        raise permission_denied(
            extra=dict(permissions=",".join(map(str, _required_permissions_to_create_variant)))
        )

    return body
