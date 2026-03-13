class UnauthorizedException(Exception):
    pass

class InvalidLoginException(UnauthorizedException):
    pass

class InvalidTokenException(UnauthorizedException):
    pass

class TokenNotFoundException(UnauthorizedException):
    pass

class TokenExpiredException(UnauthorizedException):
    pass

class ForbiddenException(Exception):
    pass

class UserException(Exception):
    pass

class PasswordDontMatchException(UserException):
    pass
