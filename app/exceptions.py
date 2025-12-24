from fastapi import HTTPException, status

InvalidLogin = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль"
)

InvalidToken = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не валиден"
)

TokenNotFound = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен отсутствует"
)

TokenExpired = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек"
)


ForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Отказано в доступе"
)

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Пользователь уже существует'
)

PasswordDontMatchException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пароли не совпадают"
)

UserNotFoundException  = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь не найден"
)