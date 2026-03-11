from db.repository.base import BaseRepository
from db.models.profiles import Position


class PositionRepository(BaseRepository):
    model = Position
