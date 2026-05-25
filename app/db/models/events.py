from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import Base



class Event(Base):
    event_type: Mapped[str]
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    access_scope: Mapped[str]
    target_id: Mapped[int]
    target_type: Mapped[str]
    message: Mapped[str | None]
    payload: Mapped[dict] = mapped_column(JSON)

    actor: Mapped["User"] = relationship(back_populates="events")