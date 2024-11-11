import uuid
import time
import pytest
import config
import asyncio
from tests import helpers
from src import permissions
from src.app import make_app
from datetime import timedelta
from src.models.base import Base
from src.util import secure_hash
from contextlib import ExitStack
from src.models import User, Token
from src.database import session_holder
from pytest_postgresql import factories
from sqlalchemy import make_url, URL, delete
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from pytest_postgresql.janitor import DatabaseJanitor
from src.ratelimit import memory_store, memory_ranking


test_db = factories.postgresql_proc()


@pytest.fixture(autouse=True)
def _app():
    with ExitStack():
        yield make_app(test_mode=True)


@pytest.fixture(autouse=True)
def _ratelimit_cleanup():
    yield
    memory_store().clear()
    memory_ranking().clear()


@pytest.fixture
def x_real_ip() -> str:
    return "test-ip"


@pytest.fixture
async def client(_app, x_real_ip):
    async with TestClient(_app) as client:
        client.headers["x-real-ip"] = x_real_ip
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
        0,
        default=True,
        title="Unverified user",
        permissions={},
    )


@pytest.fixture
async def role_user(session):
    return await helpers.create_role(
        session,
        "user",
        10,
        default=False,
        title="Regular user",
    )


@pytest.fixture
async def role_moderator(session):
    return await helpers.create_role(
        session,
        "moderator",
        20,
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
        30,
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
async def composition(session):
    return await helpers.create_composition(session)


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
            assert debug_timer.value
    """
    start = time.time()
    breaks = {}

    def add_break(label: str | None = None):
        if label is None:
            label = "BREAK_" + str(len(breaks))
        breaks[label] = (time.time() - start) * 1000

    add_break.value = False

    try:
        yield add_break
    finally:
        add_break("END")
        print("TEST TIMER")

        print("LABEL".ljust(50), "TIME TO LABEL".ljust(20), "TOOK", sep="")
        last_label_time = 0
        for label, time_ in breaks.items():
            took = time_ - last_label_time
            print(label.ljust(50), f"{time_:.4f}ms".ljust(20), f"{took:.4f}ms", sep="")
            last_label_time = time_

        print("TEST TIMER END")
