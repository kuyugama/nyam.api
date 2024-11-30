import io
import uuid
import time

import pytest
from PIL import Image

import config
import asyncio
from tests import helpers
from src import permissions
from src.app import make_app
from datetime import timedelta
from src.models.base import Base
from src.util import secure_hash
from contextlib import ExitStack
from src.database import session_holder
from pytest_postgresql import factories
from sqlalchemy import make_url, URL, delete
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from pytest_postgresql.janitor import DatabaseJanitor
from src.ratelimit import memory_store, memory_ranking

from src.models import (
    User,
    Token,
    Genre,
    Volume,
    Chapter,
    TextPage,
    ImagePage,
    UploadImage,
    Composition,
    CompositionVariant,
)


test_db = factories.postgresql_proc()


@pytest.fixture(scope="session")
def _image_file():
    image = Image.new("RGB", (100, 100), "black")
    file = io.BytesIO()
    file.name = "file.png"
    image.save(file)
    return file


@pytest.fixture
def image_file(_image_file):
    _image_file.seek(0)
    return _image_file


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
async def upload_image(session) -> UploadImage:
    return await helpers.create_upload_image(session)


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
async def role_translator(session):
    return await helpers.create_role(
        session,
        "translator",
        11,
        default=False,
        title="Translator",
        permissions={
            permissions.user.own.update_info: True,
            permissions.content_variant["*"]: True,
        },
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
            permissions.volume["*"]: True,  # noqa
            permissions.chapter["*"]: True,  # noqa
            permissions.content["*"]: True,
            permissions.page_text["*"]: True,  # noqa
            permissions.page_image["*"]: True,  # noqa
            permissions.override_author: True,
            permissions.user.update_info: True,
            permissions.content_variant["*"]: True,
            permissions.user.own.update_info: True,
            permissions.user.role_management: True,
            permissions.user.permission_management: True,
        },
    )


@pytest.fixture(scope="session")
def email_user_unverified() -> str:
    return "unverified@mail.com"


@pytest.fixture(scope="session")
def email_user_regular() -> str:
    return "user@mail.com"


@pytest.fixture(scope="session")
def email_user_moderator() -> str:
    return "moderator@mail.com"


@pytest.fixture(scope="session")
def email_user_admin() -> str:
    return "administrator@mail.com"


@pytest.fixture(scope="session")
def password_user() -> str:
    return "password"


@pytest.fixture(scope="session")
def hash_password_user(password_user: str) -> str:
    return secure_hash(password_user)


@pytest.fixture
async def user_unverified(session, hash_password_user, email_user_unverified, role_unverified):
    return await helpers.create_user(
        session,
        email_user_unverified,
        helpers.email_to_nickname(email_user_unverified),
        role_unverified,
        password_hash=hash_password_user,
    )


@pytest.fixture
async def user_regular(session, hash_password_user, email_user_regular, role_user) -> User:
    return await helpers.create_user(
        session,
        email_user_regular,
        helpers.email_to_nickname(email_user_regular),
        role_user,
        password_hash=hash_password_user,
    )


@pytest.fixture
async def user_moderator(session, hash_password_user, email_user_moderator, role_moderator) -> User:
    return await helpers.create_user(
        session,
        email_user_moderator,
        helpers.email_to_nickname(email_user_moderator),
        role_moderator,
        password_hash=hash_password_user,
    )


@pytest.fixture
async def user_admin(session, hash_password_user, email_user_admin, role_admin) -> User:
    return await helpers.create_user(
        session,
        email_user_admin,
        helpers.email_to_nickname(email_user_admin),
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
async def composition(session) -> Composition:
    return await helpers.create_composition(session)


@pytest.fixture
async def composition_variant(session, composition, user_admin) -> CompositionVariant:
    return await helpers.create_composition_variant(
        session, composition, user_admin, "variant-title", "variant-description"
    )


@pytest.fixture
async def volume(session, composition_variant) -> Volume:
    return await helpers.create_volume(session, composition_variant, 1)


@pytest.fixture
async def chapter(session, volume) -> Chapter:
    return await helpers.create_chapter(session, volume, 1)


@pytest.fixture
async def page_text(session, chapter) -> TextPage:
    return await helpers.create_text_page(session, chapter, 1, "page content")


@pytest.fixture
async def page_image(session, chapter, upload_image) -> ImagePage:
    return await helpers.create_image_page(session, chapter, 1, upload_image)


@pytest.fixture
async def genre(session) -> Genre:
    return await helpers.create_genre(
        session,
    )


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
