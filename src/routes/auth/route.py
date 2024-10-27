import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import scheme
from tasks import new_login
from src.models import User, Token
from src.database import acquire_session
from .scheme import SignUpBody, ClientInfo
from src.dependencies import require_token

from .dependencies import client_details, validate_signin, validate_signup

router = fastapi.APIRouter(
    prefix="/auth",
    tags=["Авторизація"],
)


@router.post(
    "/signup",
    response_model=scheme.Token,
    summary="Реєстрація",
    operation_id="signup",
)
async def signup(
    body: SignUpBody = Depends(validate_signup),
    session: AsyncSession = Depends(acquire_session),
) -> scheme.Token:
    user = await service.create_user(session, body)

    return await service.create_token(session, user)


@router.post(
    "/signin",
    response_model=scheme.Token,
    summary="Вхід",
    operation_id="signin",
)
async def signin(
    user: User = Depends(validate_signin),
    session: AsyncSession = Depends(acquire_session),
    client: ClientInfo = Depends(client_details),
):
    if client:
        new_login.delay(user.id, client.host)

    return await service.create_token(session, user)


@router.get(
    "/token/info",
    response_model=scheme.FullToken,
    summary="Інформація про токен",
    operation_id="token_info",
)
async def token_info(token: Token = Depends(require_token)):
    return token
