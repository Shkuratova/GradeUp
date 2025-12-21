from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import(
    create_async_engine, 
    async_sessionmaker,
    AsyncSession
)
from app.config import settings


class DataBaseHelper:
    def __init__(self):
        self.engine = create_async_engine(url=settings.db.url, echo=settings.db.echo)
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


    async def session_with_commit(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise 
            finally:
                session.close()

    
    async def session_without_commit(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise 
            finally:
                session.close()



