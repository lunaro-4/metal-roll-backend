from contextlib import asynccontextmanager
import typing
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (AsyncConnection,
                                    AsyncEngine,
                                    AsyncSession,
                                    async_sessionmaker,
                                    create_async_engine
                                    )


Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.sessionmaker: async_sessionmaker | None = None

    def init(self, db):
        self.engine = create_async_engine(db)
        self.sessionmaker = async_sessionmaker(autocommit=False,
                                               bind=self.engine)

    async def close(self):
        if self.engine is None:
            raise Exception("Session Manager is not initialised!")
        await self.engine.dispose()
        self.engine = None
        self.sessionmaker = None

    @asynccontextmanager
    async def session(self) -> typing.AsyncIterator[AsyncSession]:
        if self.sessionmaker is None:
            raise Exception("Session Manager is not initialised!")
        session = self.sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def connect(self) -> typing.AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise Exception("Session Manager is not initialised!")
        async with self.engine.begin() as connection:
            await connection
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    async def create_db_and_tables(self):
        if self.engine is None:
            raise Exception("Session Manager is not initialised!")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db_and_tables(self):
        if self.engine is None:
            raise Exception("Session Manager is not initialised!")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


session_manager = DatabaseSessionManager()


async def get_db():
    async with session_manager.session() as session:
        yield session
