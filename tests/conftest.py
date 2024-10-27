import sys
import uuid
import asyncio
import pathlib
from datetime import timedelta
from contextlib import ExitStack

sys.path[0] = str(pathlib.Path(sys.path[0]).parent)

import pytest
from src import permissions
from src.models import User, Token
from pytest_postgresql import factories
from sqlalchemy import make_url, URL, delete
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from pytest_postgresql.janitor import DatabaseJanitor

import config
from tests import helpers
from src.app import make_app
from src.models.base import Base
from src.database import session_holder

test_db = factories.postgresql_proc()


@pytest.fixture(autouse=True)
def _app():
    with ExitStack():
        yield make_app(with_lifespan=False)


@pytest.fixture
async def client(_app):
    async with TestClient(_app) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# noinspection PyShadowingNames
@pytest.fixture(scope="session", autouse=True)
async def _connection(test_db, event_loop):
    settings = config.settings

    origin_url = make_url(settings.postgresql.url)

    url = URL.create(
        drivername=origin_url.drivername,
        username=origin_url.username,
        password=origin_url.password,
        host=origin_url.host,
        port=origin_url.port,
        database=uuid.uuid4().hex,
    )

    with DatabaseJanitor(
        user=url.username,
        host=url.host,
        port=url.port,
        dbname=url.database,
        version=test_db.version,
        password=url.password,
    ):
        session_holder.init(url)
        yield
        await session_holder.close()


@pytest.fixture(autouse=True, scope="session")
async def _create_tables():
    async with session_holder.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True, scope="function")
async def _tables_cleanup(session):
    yield

    for table in Base.metadata.tables.values():
        await session.execute(delete(table))

    await session.commit()


@pytest.fixture
async def session(_connection) -> AsyncSession:
    async with session_holder.session() as session:
        yield session


@pytest.fixture
def master_key() -> str:
    return config.settings.service.master_key


@pytest.fixture
async def role_unverified(session):
    return await helpers.create_role(
        session,
        "unverified",
        default=True,
        description="Unverified user",
        permissions={},
    )


@pytest.fixture
async def role_user(session):
    return await helpers.create_role(
        session,
        "user",
        default=False,
        description="Regular user",
    )


@pytest.fixture
async def role_moderator(session):
    return await helpers.create_role(
        session,
        "moderator",
        default=False,
        description="Moderator",
        permissions={
            permissions.user.update_info: True,
            permissions.user.own.update_info: True,
        },
    )


@pytest.fixture
async def role_admin(session):
    return await helpers.create_role(
        session,
        "admin",
        default=False,
        description="Administrator",
        permissions={
            permissions.user.update_info: True,
            permissions.user.own.update_info: True,
            permissions.user.role_management: True,
            permissions.user.permission_management: True,
        },
    )


@pytest.fixture
def user_password() -> str:
    return "password"


@pytest.fixture
async def user_unverified(session, user_password, role_unverified):
    return await helpers.create_user(
        session,
        "unverified@mail.com",
        "unverified",
        user_password,
        role_unverified,
    )


@pytest.fixture
async def user_regular(session, user_password, role_user) -> User:
    return await helpers.create_user(session, "user@mail.com", "user", user_password, role_user)


@pytest.fixture
async def user_moderator(session, user_password, role_moderator) -> User:
    return await helpers.create_user(
        session,
        "moderator@mail.com",
        "moderator",
        user_password,
        role_moderator,
    )


@pytest.fixture
async def user_admin(session, user_password, role_admin) -> User:
    return await helpers.create_user(session, "admin@mail.com", "admin", user_password, role_admin)


@pytest.fixture
async def token_regular(session, user_regular) -> Token:
    return await helpers.create_token(session, user_regular)


@pytest.fixture
async def token_moderator(session, user_moderator) -> Token:
    return await helpers.create_token(session, user_moderator)


@pytest.fixture
async def token_admin(session, user_admin) -> Token:
    return await helpers.create_token(session, user_admin)


@pytest.fixture
async def expired_token(session, user_regular) -> Token:
    return await helpers.create_token(session, user_regular, valid_for=timedelta(minutes=-1))
