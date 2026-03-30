from fastapi import HTTPException, status, Depends
from functools import wraps

from dependencies.auth import get_current_user
from exceptions.user import (
    UnauthorizedException,
    UserException,
)
from exceptions.common import AlreadyExistException, NotFoundException, ValidationError
from schemas.users import UserInfo

def exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (UnauthorizedException, ) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
            )
        except NotFoundException as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            )

        except AlreadyExistException as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
        except (UserException, ValidationError) as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    return wrapper


def check_role(required_roles: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: UserInfo = Depends(get_current_user), **kwargs):
            print(current_user.model_dump())
            if not current_user.role_name in required_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Отказано в доступе.")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
