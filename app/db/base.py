from sqlalchemy import select
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

class BaseDAO:
    model = None 

    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session
    

    async def  get_all(self):
        stmt = select(self.model)
        try:
            res = self._sesison.execute(stmt)
            return res.scalars().all()
        except SQLAlchemyError as e:
            print(e)
            raise 
