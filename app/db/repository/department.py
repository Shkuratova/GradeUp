from db.repository.base import BaseRepository
from db.models import Department


class DepartmentRepository(BaseRepository):
    model = Department

def department_repository_factory(session):
    return DepartmentRepository(session)