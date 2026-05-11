from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from db.repository import BaseRepository
from db.models import (
    UserProfile,
    User,
    UserLevel,
    ProfileLevel,
    ProfileLevelVersion,
    Profile, Department,
)


class UserProfileRepository(BaseRepository):
    model = UserProfile

    async def get_all_with_progress(self):

        total_lvl_subq = (
            select(
                ProfileLevel.profile_id, func.count(ProfileLevel.id).label("total_cnt")
            )
            .where(ProfileLevel.is_active == True)
            .group_by(ProfileLevel.profile_id)
            .subquery()
        )

        completed_levels = (
            select(UserLevel.user_id, func.count(UserLevel.id).label("completed_cnt"))
            .where(UserLevel.is_closed == True)
            .group_by(UserLevel.user_id)
            .subquery()
        )
        stmt = (
            select(
                UserProfile.id.label("id"),
                UserProfile.user_id.label("user_id"),
                User.first_name.label("first_name"),
                User.last_name.label("last_name"),
                func.coalesce(User.patronymic, "").label("patronymic"),
                User.email.label("email"),
                User.position.label("position"),
                Profile.title.label("profile_title"),
                Department.id.label("department_id"),
                Department.department_name.label("department_name"),
                total_lvl_subq.c.total_cnt,
                func.coalesce(completed_levels.c.completed_cnt, 0).label(
                    "completed_cnt"
                ),
            )
            .select_from(UserProfile)
            .join(Profile, Profile.id == UserProfile.profile_id)
            .join(User, User.id == UserProfile.user_id)
            .outerjoin(Department, Department.id == User.department_id)
            .outerjoin(
                total_lvl_subq,
                total_lvl_subq.c.profile_id == UserProfile.profile_id,
            )
            .outerjoin(
                completed_levels,
                completed_levels.c.user_id == UserProfile.user_id,
            )
        )
        res = await self._session.execute(stmt)
        return res.all()


# UserProfile -> Profile -> LastLevels (where last_version)
# UserProfile -> Users -> UserLevels (where is_accepted == True)
# left join last_levels + user_levels
# Посчитать процент прохождения как кол-во пройденных на кол-во уровней
