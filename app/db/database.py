from typing import Annotated
from datetime import datetime
import re 
from sqlalchemy import func, TIMESTAMP, Integer
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    declared_attr,
)
from app.config import settings


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', cls.__name__).lower() + 's'
    


    