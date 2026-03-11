from db.repository.base import BaseRepository
from db.models import  Profile, ProfileLevel, Level


class ProfileRepository(BaseRepository):
    model = Profile

class LevelRepository(BaseRepository):
    model = Level

class ProfileLevelRepository(BaseRepository):
    model = ProfileLevel