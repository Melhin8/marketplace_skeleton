from functools import lru_cache
from pydantic import BaseSettings, PostgresDsn

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncConnection
from sqlalchemy.orm import declarative_base, sessionmaker


class Settings(BaseSettings):
    POSTGRES_URI: PostgresDsn


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings


Base = declarative_base()


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None
    
    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            get_settings().POSTGRES_URI,
            future=True,
            echo=True,
        )
        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )()
    
    async def close(self):
        await self._engine.dispose()


db = AsyncDatabaseSession()