import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


class AsyncDatabaseConnection:
    def __init__(self):
        self._session = None
        self._engine = None

    @property
    def session(self) -> AsyncSession:
        return self._session

    def init(self):
        self._engine = create_async_engine(
            url="sqlite+aiosqlite:///db.sqlite3",
        )
        self._session = AsyncSession(self._engine)


db = AsyncDatabaseConnection()
