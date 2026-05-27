import logging
logger = logging.getLogger(__name__)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.models import Event, User
from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler


class EventRepository(BaseRepository):
    model = Event

    @db_exception_handler
    async def get_events(self, filter_dict: dict):
        start_date = filter_dict.pop("start_date", None)
        end_date = filter_dict.pop("end_date", None)
        stmt = select(Event).filter_by(**filter_dict)

        if start_date and end_date:
            stmt = stmt.where(Event.created_at.between(start_date, end_date))
        elif start_date:
            stmt = stmt.where(Event.created_at >= start_date)
        elif end_date:
            stmt = stmt.where(Event.created_at <= end_date)
        stmt = stmt.options(
            joinedload(Event.actor)
        ).order_by(Event.created_at.desc())
        res = await self._session.execute(stmt)

        logger.info("Выполнен запрос на получения журнала событий")
        return res.scalars().all()
