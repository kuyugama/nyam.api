from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import permissions
from src.models import Composition
from src.util import PermissionChecker
from src.database import acquire_session
from ..dependencies import require_provider
from src.scheme import define_error_category
from .scheme import CreateCompositionVariantBody
from src.content_providers import BaseContentProvider
from src.dependencies import interactive_require_permissions

define_error = define_error_category("content/composition")
provider_composition_not_found = define_error(
    "provider-composition-not-found", "Provider composition not found", 404
)
composition_already_exists = define_error(
    "composition-already-exists", "Composition already exists", 400
)
composition_not_found = define_error("composition-not-found", "Composition not found", 404)


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


async def validate_publish_variant(
    body: CreateCompositionVariantBody,
    origin: Composition = Depends(require_composition),
    has_permission: PermissionChecker = interactive_require_permissions,
):
    has_permission(permissions.content[origin.style].update)

    return body
