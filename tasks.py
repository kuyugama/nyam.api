import inspect
from datetime import timedelta
from functools import lru_cache, wraps

import dramatiq
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from ua_parser import user_agent_parser
from periodiq import PeriodiqMiddleware, cron
from dramatiq.brokers.redis import RedisBroker
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings

broker = RedisBroker(url=settings.redis.url)
broker.add_middleware(dramatiq.middleware.asyncio.AsyncIO())
broker.add_middleware(PeriodiqMiddleware())
dramatiq.set_broker(broker)


def log(*args, sep: str = " ", end: str = "\n"):
    stack = inspect.stack()
    caller = stack[1]
    ctx = caller.function + " >>>"

    print(f"[+] {ctx}".strip(), *args, sep=sep, end=end)


@lru_cache(maxsize=-1)
def init_db():
    from src.database import session_holder

    session_holder.init(settings.postgresql.url)

    return session_holder


def get_session() -> AsyncSession:
    return init_db().session()


def with_session(func):
    if not inspect.iscoroutinefunction(func):
        raise TypeError("Database sessions allowed only in async functions")

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with get_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper


@dramatiq.actor(max_retries=3)
@with_session
async def new_login(session: AsyncSession, user_id: int, address: str, agent: str | None):
    from src.models import User, Token
    from src.util import now

    now = now()

    agent_data = user_agent_parser.Parse(agent)

    user = await session.get(User, user_id, options=(joinedload(User.tokens),))

    assert isinstance(user, User), f"Non-User instance returned by sqlalchemy - {user!r}[{user}]"

    log("Address:", address)
    log(f"OS:", agent_data["os"])
    log(f"Device:", agent_data["device"])
    log(f"Client:", agent_data["user_agent"])
    log("User:", user.id, "Nickname:", user.nickname)
    log("Tokens count:", len(user.tokens))

    older_and_active_tokens = await session.scalars(
        select(Token).filter(
            Token.created_at <= now - timedelta(hours=24),
            Token.expire_at > now,
            Token.owner_id == user_id,
        )
    )

    # There should be logic for sending notification to specific tokens about actions
    for token in older_and_active_tokens:
        log(f"Notifying token {token.id} about new login")


@dramatiq.actor
@with_session
async def user_nickname_updated(
    session: AsyncSession, user_id: str, before: str, after: str, updated_by: int | None = None
) -> None:
    from src.models import User

    user = await session.get(User, user_id)

    if user is None:
        return

    # There should be logic to save up to 10 nickname changes per user
    log("User:", user.id, "Nickname:", user.nickname)
    log("Before:", before)
    log("After:", after)
    log("Updated by:", updated_by)


@dramatiq.actor(periodic=cron("0,*/10 * * * *"))
@with_session
async def periodiq_drop_expired_tokens(session: AsyncSession):
    from src.service import drop_expired_tokens

    log("Dropping all expired tokens")
    await drop_expired_tokens(session)
