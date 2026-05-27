from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload

from db.models import (
    UserProfile,
    UserLevel,
    ProfileLevel,
)
from db.repository import BaseRepository
from db.repository.decorators import db_exception_handler

import logging

logger = logging.getLogger(__name__)


class UserLevelRepository(BaseRepository):
    model = UserLevel

    @db_exception_handler
    async def get_current_lvl(self, user_id: int):
        stmt = (
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                joinedload(UserProfile.current_level).load_only(
                    ProfileLevel.id, ProfileLevel.num, ProfileLevel.level_name
                ),
            )
        )
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение текущего уровня профиля пользователяя"
        )
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_by_level_id(self, user_id: int, level_id: int):
        stmt = select(UserLevel).where(
            UserLevel.profile_level_id == level_id, UserLevel.user_id == user_id
        )
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение уровня пользователя по id (user_id=%s, level_id=%s)",
            user_id,
            level_id,
        )
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_level_count(self, levels_id: list[int]):
        stmt = select(func.count(UserLevel.user_id)).where(
            UserLevel.profile_level_id.in_(levels_id)
        )
        res = await self._session.execute(stmt)

        logger.info("Выполнен запрос на получение количества уровней пользователей по списку id уровней")
        return res.scalar_one_or_none()

    @db_exception_handler
    async def delete_by_user(self, user_id):
        stmt = delete(UserLevel).where(UserLevel.user_id == user_id)
        res = await self._session.execute(stmt)

        logger.info("Удаление уровня пользователя по id (user_id=%s)", user_id)
        return res.rowcount

    @db_exception_handler
    async def get_all_by_user(self, user_id: int):
        stmt = select(UserLevel).where(UserLevel.user_id == user_id)
        res = await self._session.execute(stmt)

        logger.info("Выполнен запрос на получение уровней пользователя (user_id=%s)", user_id)
        return res.scalars().all()
