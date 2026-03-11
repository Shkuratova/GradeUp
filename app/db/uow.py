from contextlib import asynccontextmanager
from db.database import async_session


class UnitOfWork:
    def __init__(self):
        self.session = async_session()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()


@asynccontextmanager
async def unit_of_work():
    uow = UnitOfWork()
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()
