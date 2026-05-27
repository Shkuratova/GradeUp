from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

import logging
logger = logging.getLogger(__name__)


def db_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Integrity error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Database constraint violation",
            ) from e
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal database error",
            ) from e
    return wrapper
