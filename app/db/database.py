from datetime import datetime
import re
from sqlalchemy import func, TIMESTAMP, Integer, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    sessionmaker,
    DeclarativeBase,
    declared_attr,
)
from config import settings


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r"([a-z])([A-Z])", r"\1_\2", cls.__name__).lower() + "s"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self, exclude_none: bool = False) -> dict:
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)
            if not exclude_none or value is not None:
                result[column.key] = value

        return result


engine = create_async_engine(settings.db.url, echo=settings.db.echo)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def get_db():
    db = async_session
    try:
        yield db
    finally:
        db.close()
