from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src import oauth_providers
from src.service import get_lowest_role
from src.database import acquire_session
from src.scheme import define_error_category
from ..dependencies import default_role_not_exist

define_error = define_error_category("oauth")

provider_not_found = define_error("provider-not-found", "OAuth provider not found", 404)


@provider_not_found.mark
def require_oauth_provider(identifier: str) -> oauth_providers.BaseOAuthProvider:
    provider = oauth_providers.get_provider_instance(identifier)

    if not provider:
        raise provider_not_found

    return provider


async def require_oauth_token(
    request: Request,
    oauth_provider: oauth_providers.BaseOAuthProvider = Depends(require_oauth_provider),
) -> oauth_providers.OAuthToken:
    return await oauth_provider.callback(dict(request.query_params))


async def require_oauth_user(
    token: oauth_providers.OAuthToken = Depends(require_oauth_token),
    oauth_provider: oauth_providers.BaseOAuthProvider = Depends(require_oauth_provider),
) -> oauth_providers.OAuthUser:
    return await oauth_provider.get_user(token)


@default_role_not_exist.mark
async def require_default_role(session: AsyncSession = Depends(acquire_session)):
    role = await get_lowest_role(session)
    if role is None:
        raise default_role_not_exist

    return role
