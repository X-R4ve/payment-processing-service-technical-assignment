from os import getenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, \
    async_sessionmaker, AsyncSession


class DatabaseConnection:
    def __init__(self, db_url: str, expire_on_commit: bool = False):
        self._db_url = db_url
        self._expire_on_commit = expire_on_commit

        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker | None = None

    def db_url(self) -> str:
        return self._db_url

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(url=self._db_url)
        return self._engine

    @property
    def session_maker(self) -> async_sessionmaker:
        if self._session_maker is None:
            self._session_maker = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=self._expire_on_commit
            )
        return self._session_maker

    def new_session(self) -> AsyncSession:
        return self.session_maker()

    async def close(self):
        if self._engine is not None:
            await self._engine.dispose()
        self._engine = None
        self._session_maker = None
