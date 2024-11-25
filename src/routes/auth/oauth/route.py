from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Role
from ..service import create_token
from src import scheme, oauth_providers
from src.database import acquire_session
from src.routes.auth.oauth import service
from src.oauth_providers import OAuthToken, OAuthUser, BaseOAuthProvider

from src.routes.auth.oauth.dependencies import (
    require_oauth_user,
    require_oauth_token,
    require_oauth_provider,
    require_default_role,
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
        await service.save_oauth_token(session, token, identity)

    return await create_token(session, identity.user)


@router.get(
    "/{identifier}/url",
    summary="Отримати посилання входу через OAuth провайдер",
    operation_id="get_oauth_url",
    response_model=str,
)
def get_oauth_url(provider: BaseOAuthProvider = Depends(require_oauth_provider)):
    return provider.get_url()
