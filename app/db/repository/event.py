from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.repository.base import BaseRepository
from db.models import Event, User


class EventRepository(BaseRepository):
    model = Event

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
            joinedload(Event.actor).load_only(
                User.first_name, User.last_name, User.patronymic, User.email
            )
        ).order_by(Event.created_at.desc())
        res = await self._session.execute(stmt)
        return res.scalars().all()
