import sys
import time
import uuid
import asyncio
import pathlib
from datetime import timedelta
from contextlib import ExitStack

sys.path[0] = str(pathlib.Path(sys.path[0]).parent)

import pytest
from pytest_postgresql import factories
from sqlalchemy import make_url, URL, delete
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from pytest_postgresql.janitor import DatabaseJanitor

import config
from tests import helpers
from src import permissions
from src.app import make_app
from src.util import secure_hash
from src.models.base import Base
from src.models import User, Token
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
        title="Unverified user",
        permissions={},
    )


@pytest.fixture
async def role_user(session):
    return await helpers.create_role(
        session,
        "user",
        default=False,
        title="Regular user",
    )


@pytest.fixture
async def role_moderator(session):
    return await helpers.create_role(
        session,
        "moderator",
        default=False,
        title="Moderator",
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
        title="Administrator",
        permissions={
            permissions.user.update_info: True,
            permissions.user.own.update_info: True,
            permissions.user.role_management: True,
            permissions.user.permission_management: True,
        },
    )


@pytest.fixture(scope="session")
def password_user() -> str:
    return "password"


@pytest.fixture(scope="session")
def hash_password_user(password_user: str) -> str:
    return secure_hash(password_user)


@pytest.fixture
async def user_unverified(session, hash_password_user, role_unverified):
    return await helpers.create_user(
        session,
        "unverified@mail.com",
        "unverified",
        role_unverified,
        password_hash=hash_password_user,
    )


@pytest.fixture
async def user_regular(session, hash_password_user, role_user) -> User:
    return await helpers.create_user(
        session,
        "user@mail.com",
        "regular_user",
        role_user,
        password_hash=hash_password_user,
    )


@pytest.fixture
async def user_moderator(session, hash_password_user, role_moderator) -> User:
    return await helpers.create_user(
        session,
        "moderator@mail.com",
        "moderator",
        role_moderator,
        password_hash=hash_password_user,
    )


@pytest.fixture
async def user_admin(session, hash_password_user, role_admin) -> User:
    return await helpers.create_user(
        session,
        "admin@mail.com",
        "administrator",
        role_admin,
        password_hash=hash_password_user,
    )


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


@pytest.fixture
def debug_timer():
    """
    Used to debug tests with anomaly slow execution time.

    Usage:
    ::
        def test_something(debug_timer):
            debug_timer("pre fibonacci")
            fib = fibonacci(1024)
            debug_timer("after fibonacci")

            # To see timer results in teardown output
            assert False
    """
    start = time.time()
    breaks = {}

    def add_break(label: str | None = None):
        if label is None:
            label = "BREAK_" + str(len(breaks))
        breaks[label] = (time.time() - start) * 1000

    try:
        yield add_break
    finally:
        end = time.time()
        print("TEST TIMER")

        for label, time_ in breaks.items():
            print(f"TIME TO {label}:", time_, "ms")

        print("EXECUTION TIME:", (end - start) * 1000, "ms")
        print("TEST TIMER END")
