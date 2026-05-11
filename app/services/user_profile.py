from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import UserProfileRepository, LevelRepository
from exceptions.common import NotFoundException
from schemas.user_profile import UserProfileAdd, UserProfileProgressList
from services import BaseService, UserService, ProfileService

class UserProfileService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = UserProfileRepository(self.session)
        self.level_repository = LevelRepository(self.session)

    async def get_all_with_progress(self):
        user_profiles = await self.repository.get_all_with_progress()
        return user_profiles

    async def create(self, model: UserProfileAdd):
        profile = await ProfileService(self.session).get_by_id(model.profile_id)
        user = await UserService(self.session).get_by_id(model.user_id)
        current_lvl = await self.level_repository.get_last_level_by_num(profile_id=model.profile_id, level_num=1)
        if current_lvl is None:
            raise NotFoundException("Нет доступного уровня внутри профиля.")

        data_dict = model.model_dump()

        user_profile = await self.repository.add({**data_dict, 'current_level_id': current_lvl})
        return user_profile

    async def update(self):
        pass

    async def delete(self):
        pass

    async def status(self):
        pass
