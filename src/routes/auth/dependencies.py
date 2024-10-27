from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import scheme
from src.database import acquire_session
from src.util import verify_payload, has_errors

from .scheme import (
    ClientInfo,
    SignUpBody,
    SignInBody,
    SignInEmailBody,
    SignInNicknameBody,
)
from ...service import get_default_role

define_error = scheme.define_error_category("auth")
default_role_not_exist = scheme.define_error(
    "roles",
    "default-role-not-exist",
    "Default role not found to create user",
    500,
)
email_occupied = define_error("email-occupied", "Email occupied", 400)
nickname_occupied = define_error("nickname-occupied", "Nickname occupied", 400)
user_not_found = define_error("user-not-found", "User not found", 404)
password_incorrect = define_error("password-incorrect", "Password incorrect", 400)


def client_details(request: Request) -> ClientInfo:
    if request.client:
        return ClientInfo(request.client.host)

    if "x-forwarder-for" in request.headers:
        return ClientInfo(request.headers["x-forwarder-for"])

    if "x-real-ip" in request.headers:
        return ClientInfo(request.headers["x-real-ip"])


@has_errors(email_occupied, nickname_occupied, default_role_not_exist)
async def validate_signup(
    body: SignUpBody, session: AsyncSession = Depends(acquire_session)
) -> SignUpBody:
    if await get_default_role(session) is None:
        raise default_role_not_exist

    if await service.get_user_by_email(session, body.email) is not None:
        raise email_occupied

    if await service.get_user_by_nickname(session, body.nickname) is not None:
        raise nickname_occupied

    return body


@has_errors(password_incorrect, user_not_found)
async def validate_signin(body: SignInBody, session: AsyncSession = Depends(acquire_session)):
    user = None
    if isinstance(body, SignInEmailBody):
        user = await service.get_user_by_email(session, body.email)

    if isinstance(body, SignInNicknameBody):
        user = await service.get_user_by_nickname(session, body.nickname)

    if user is None:
        raise user_not_found

    if not verify_payload(body.password, user.password_hash):
        raise password_incorrect

    return user
