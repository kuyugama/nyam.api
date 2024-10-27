import contextlib
from typing import AsyncIterator, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    AsyncConnection,
    async_sessionmaker,
    create_async_engine,
)


class SessionHolder:
    def __init__(self):
        self._session_maker: async_sessionmaker | None = None
        self._engine: AsyncEngine | None = None
        self._url: str | None = None

    def init(self, url: str):
        self._url = url
        self._engine = create_async_engine(url, echo=False)
        self._session_maker = async_sessionmaker(
            autocommit=False,
            expire_on_commit=False,
            bind=self._engine,
        )

    async def close(self):
        if self._engine is None:
            raise RuntimeError("SessionHolder is not initialized")

        await self._engine.dispose()

        self._session_maker = None
        self._engine = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise RuntimeError("SessionHolder is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise RuntimeError("SessionHolder is not initialized")

        session = self._session_maker()

        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


session_holder = SessionHolder()


async def acquire_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_holder.session() as session:
        yield session
