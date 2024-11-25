import secrets
from dataclasses import replace

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.service import get_user_by_nickname
from src.routes.auth.service import get_user_by_email
from src.oauth_providers import OAuthUser, OAuthToken
from src.models import OAuthIdentity, User, ThirdpartyToken, Role


async def get_oauth_identity(
    session: AsyncSession, provider: str, user: OAuthUser
) -> OAuthIdentity:
    return await session.scalar(
        select(OAuthIdentity)
        .filter_by(provider=provider, provider_user=user.id)
        .options(joinedload(OAuthIdentity.user))
    )


async def create_oauth_user(
    session: AsyncSession, provider: str, oauth_user: OAuthUser, role: Role
) -> OAuthIdentity:

    user = None
    # If user with that email already exists - use this user
    if oauth_user.email:
        user = await get_user_by_email(session, oauth_user.email)

    if user is None:
        for i in range(4):
            # If user with that nickname does not exist - break
            if not await get_user_by_nickname(session, oauth_user.nickname):
                break

            # If it is first iteration - add _ to end of username to split nickname and our random chars
            if i == 0:
                oauth_user = replace(oauth_user, nickname=oauth_user.nickname + "_")

            # Add 4 random chars to end of username
            oauth_user = replace(oauth_user, nickname=oauth_user.nickname + secrets.token_hex(4))
        else:
            # Generate completely new username, if steps above doesn't help make it unique
            oauth_user = replace(oauth_user, nickname=secrets.token_hex(12))

        user = User(email=oauth_user.email, nickname=oauth_user.nickname, role=role)

        session.add(user)

    identity = OAuthIdentity(
        user=user,
        provider=provider,
        provider_user=oauth_user.id,
    )

    session.add(identity)

    await session.commit()

    return identity


async def save_oauth_token(
    session: AsyncSession, token: OAuthToken, identity: OAuthIdentity
) -> ThirdpartyToken:
    thirdparty_token = ThirdpartyToken(
        identity=identity,
        access_token=token.access_token,
        token_type=token.token_type,
        refresh_token=token.refresh_token,
        refresh_after=token.refresh_after,
        refresh_before=token.refresh_before,
    )

    session.add(thirdparty_token)

    await session.commit()

    return thirdparty_token
