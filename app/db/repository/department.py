from db.repository.base import BaseRepository
from db.models import Department


class DepartmentRepository(BaseRepository):
    model = Department

