from sqlalchemy import select
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def get_one_or_none_by_id(self, data_id: int):
        try:
            stmt = select(self.model).filter_by(id=data_id)
            res = await self._session.execute(stmt)
            row = res.scalar_one_or_none()
            return row
        except SQLAlchemyError as e:
            print(e)
            raise

    async def get_one_or_none(self, filter_by: BaseModel):
        filter_dict = filter_by.model_dump(exclude_unset=True)
        try:
            stmt = select(self.model).filter_by(**filter_dict)
            res = await self._session.execute(stmt)
            row = res.scalar_one_or_none()
            return row
        except SQLAlchemyError as e:
            print(e)
            raise

    async def get_all(self):
        stmt = select(self.model)
        try:
            res = self._sesison.execute(stmt)
            return res.scalars().all()
        except SQLAlchemyError as e:
            print(e)
            raise
