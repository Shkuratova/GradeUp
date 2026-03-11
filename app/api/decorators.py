from fastapi import HTTPException, status
from functools import wraps
from exceptions.user import (
    UnauthorizedException,
    UserException,
    UserAlreadyExistException,
    UserNotFoundException,
    ForbiddenException,
)


def auth_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (UnauthorizedException, ) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
            )
        except UserNotFoundException as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            )
        except ForbiddenException as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
            )
        except UserAlreadyExistException as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
        except UserException as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    return wrapper
