from sqlalchemy.exc import SQLAlchemyError
from functools import wraps

def db_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            print(e)
            raise

    return wrapper