from app.db import BaseDAO
from app.auth.models import User


class UserDAO(BaseDAO):
    model = User
    