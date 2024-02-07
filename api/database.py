from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine, AsyncConnection
from config import get_config


class SessionManagerNotInitialized(Exception):
    """ Raised when user try to interact with AsyncDBSessionManager before initialization  """

    def __init__(self):
        msg = """AsyncDBSessionManager is not initialized. Init instance with function `init()`."""
        super().__init__(msg)


class AsyncDBSessionManager:
    """ Class for async connection to database """

    def __init__(self, db_url: str, expire_on_commit: bool = True, autoflush: bool = True):
        self.db_url = db_url
        self.session_settings = {
            'expire_on_commit': expire_on_commit,
            'autoflush': autoflush,
        }
        self.engine_settings = {}

        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None
        self.init()

    def init(self):
        """ Initialize session manager. Create async engine and async session maker """
        self._engine = create_async_engine(self.db_url, connect_args=self.engine_settings)
        self._session_maker = async_sessionmaker(self._engine, **self.session_settings)

    def raise_if_not_initialized(self) -> None:
        """ Check, if instance was initialized. If not, raise error """
        if self._engine is None or self._session_maker is None:
            raise SessionManagerNotInitialized

    async def close(self):
        """ Dispose engine and close all connection """
        self.raise_if_not_initialized()
        await self._engine.dispose()
        self._engine = None
        self._session_maker = None

    @asynccontextmanager
    async def create_connect(self) -> AsyncIterator[AsyncConnection]:
        """ Create and return connection to database via engine. If error, called rollback()  """
        self.raise_if_not_initialized()

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def create_session(self) -> AsyncIterator[AsyncSession]:
        """ Create and return session to interact with database via ORM. If error, called rollback()  """
        self.raise_if_not_initialized()

        session = self._session_maker()
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            await session.close()


session_manager = AsyncDBSessionManager(db_url=get_config().db.url)
