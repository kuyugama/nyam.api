from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Role
from ..service import create_token
from .scheme import FullOAuthProvider
from src import scheme, oauth_providers
from src.database import acquire_session
from src.routes.auth.oauth import service
from tasks import refresh_thirdparty_token
from src.oauth_providers import OAuthToken, OAuthUser, BaseOAuthProvider

from src.routes.auth.oauth.dependencies import (
    require_oauth_user,
    require_oauth_token,
    require_default_role,
    require_oauth_provider,
)

router = APIRouter(prefix="/oauth")


@router.get(
    "/providers",
    summary="Отримати всі підтримувані провайдери OAuth",
    response_model=list[scheme.OAuthProvider],
    operation_id="list_oauth_providers",
)
def list_oauth_providers():
    return oauth_providers.provider_registry.values()


@router.post(
    "/{identifier}",
    summary="Увійти за допомогою OAuth провайдеру",
    operation_id="signin_using_oauth",
    response_model=scheme.Token,
)
async def signin_using_oauth(
    identifier: str,
    role: Role = Depends(require_default_role),
    token: OAuthToken = Depends(require_oauth_token),
    user: OAuthUser = Depends(require_oauth_user),
    session: AsyncSession = Depends(acquire_session),
):
    identity = await service.get_oauth_identity(
        session=session,
        provider=identifier,
        user=user,
    )

    if not identity:
        identity = await service.create_oauth_user(
            session=session, provider=identifier, oauth_user=user, role=role
        )

    if token.save_token:
        thirdparty = await service.save_oauth_token(session, token, identity)

        refresh_thirdparty_token.send_with_options(
            kwargs=dict(token_id=thirdparty.id),
            delay=thirdparty.created_at - thirdparty.refresh_after,
        )

    return await create_token(session, identity.user)


@router.get(
    "/{identifier}",
    summary="Отримати інформацію про OAuth провайдера",
    operation_id="get_oauth_provider",
    response_model=FullOAuthProvider,
)
def get_oauth_url(identifier: str, provider: BaseOAuthProvider = Depends(require_oauth_provider)):
    entry = oauth_providers.get_provider(identifier)
    assert entry is not None

    return dict(
        url=provider.get_url(),
        name=entry["name"],
        description=entry["description"],
        identifier=identifier,
    )
