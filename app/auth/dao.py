from app.db import BaseDAO
from .models import User, Role, Department, Position


class UserDAO(BaseDAO):
    model = User


class DepartmentDAO(BaseDAO):
    model = Department


class RoleDAO(BaseDAO):
    model = Role


class PositionDAO(BaseDAO):
    model = Position
