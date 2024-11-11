import fastapi
from fastapi import Depends
from datetime import timedelta
from ratelimit import ratelimit, LimitRule
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import scheme
from tasks import new_login
from .scheme import SignUpBody
from src.models import User, Token
from src.database import acquire_session
from src.dependencies import require_token, client_details

from .dependencies import validate_signin, validate_signup

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
    dependencies=[
        Depends(
            ratelimit(
                LimitRule(
                    hits=30,
                    batch_time=timedelta(minutes=5).total_seconds(),
                    block_time=timedelta(minutes=5).total_seconds(),
                ),
                LimitRule(
                    hits=30,
                    batch_time=timedelta(minutes=5).total_seconds(),
                    block_time=timedelta(minutes=10).total_seconds(),
                ),
            )
        )
    ],
)
async def signin(
    user: User = Depends(validate_signin),
    session: AsyncSession = Depends(acquire_session),
    client: scheme.ClientInfo = Depends(client_details),
):
    if client:
        new_login.send(user.id, client.host, client.agent)

    return await service.create_token(session, user)


@router.get(
    "/token/info",
    response_model=scheme.FullToken,
    summary="Інформація про токен",
    operation_id="token_info",
)
async def token_info(token: Token = Depends(require_token)):
    return token
