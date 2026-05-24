from sqlalchemy import select, func, and_, exists, insert, literal, delete
from sqlalchemy.orm import joinedload, selectinload, with_loader_criteria

from db.models.skills import StageVersion
from db.models.user_profiles import UserSkill
from db.repository import BaseRepository
from db.models import (
    UserProfile,
    User,
    UserLevel,
    ProfileLevel,
    Profile,
    Department,
    UserStage,
    Skill,
    Stage,
    LevelSkill,
    Role,
)
from schemas.skills import SkillStages


class UserProfileRepository(BaseRepository):
    model = UserProfile

    async def get_all_with_progress(self, filter_dict: dict):

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
                User.id.label("user_id"),
                User.first_name.label("first_name"),
                User.last_name.label("last_name"),
                func.coalesce(User.patronymic, "").label("patronymic"),
                User.email.label("email"),
                User.position.label("position"),
                UserProfile.id.label("id"),
                Profile.id.label("profile_id"),
                Profile.title.label("profile_title"),
                Department.id.label("department_id"),
                Department.department_name.label("department_name"),
                Role.id.label("role_id"),
                Role.role_name,
                total_lvl_subq.c.total_cnt,
                func.coalesce(completed_levels.c.completed_cnt, 0).label(
                    "completed_cnt"
                ),
            )
            .select_from(User)
            .outerjoin(UserProfile, UserProfile.user_id == User.id)
            .outerjoin(Profile, Profile.id == UserProfile.profile_id)
            .outerjoin(Department, Department.id == User.department_id)
            .join(Role, Role.id == User.role_id)
            .outerjoin(
                total_lvl_subq,
                total_lvl_subq.c.profile_id == UserProfile.profile_id,
            )
            .outerjoin(
                completed_levels,
                completed_levels.c.user_id == User.id,
            )
        )

        res = await self._session.execute(stmt)
        return res.all()

    async def get_profile(self, user_id: int):
        stmt = (
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                joinedload(UserProfile.profile).load_only(Profile.id, Profile.title)
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_profile_progress(self, user_id: int):
        stmt = (
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                joinedload(UserProfile.user)
                .load_only(User.id)
                .selectinload(User.user_skills)
                .load_only(UserSkill.skill_id, UserSkill.is_accepted)
                .selectinload(UserSkill.stages)
                .load_only(
                    UserStage.id,
                    UserStage.updated_at,
                    UserStage.is_accepted,
                    UserStage.comment,
                )
                .joinedload(UserStage.stage_version)
                .load_only(StageVersion.stage_id)
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_available_skills(self, user_id: int):
        stmt = (
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                joinedload(UserProfile.current_level)
                .selectinload(ProfileLevel.skills)
                .load_only(LevelSkill.id),
                joinedload(UserProfile.current_level)
                .selectinload(ProfileLevel.skills)
                .joinedload(LevelSkill.skill)
                .load_only(Skill.id, Skill.title),
                joinedload(UserProfile.current_level)
                .selectinload(ProfileLevel.skills)
                .joinedload(LevelSkill.skill)
                .selectinload(Skill.stages)
                .load_only(Stage.id, Stage.confirmation_type),
                with_loader_criteria(
                    Stage,
                    ~exists(
                        select(1)
                        .select_from(UserStage)
                        .join(
                            StageVersion,
                            StageVersion.id == UserStage.stage_version_id,
                        )
                        .join(
                            UserSkill,
                            UserSkill.id == UserStage.user_skill_id,
                        )
                        .where(
                            and_(
                                StageVersion.stage_id == Stage.id,
                                UserSkill.user_id == user_id,
                                UserStage.is_accepted.is_(True),
                            )
                        )
                    ).correlate(Stage),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    Stage,
                    ~exists(
                        select(1)
                        .select_from(UserStage)
                        .join(
                            StageVersion,
                            StageVersion.id == UserStage.stage_version_id,
                        )
                        .join(
                            UserSkill,
                            UserSkill.id == UserStage.user_skill_id,
                        )
                        .join(
                            UserLevel,
                            UserLevel.id == UserSkill.user_level_id,
                        )
                        .where(
                            and_(
                                StageVersion.stage_id == Stage.id,
                                UserLevel.user_id == user_id,
                                UserStage.is_accepted.is_(True),
                            )
                        )
                    ).correlate(Stage),
                    include_aliases=True,
                ),
            )
        )

        res = await self._session.execute(stmt)

        return res.scalar_one_or_none()

    async def has_available_stage(self, user_id: int, stage_id: int) -> bool:
        stmt = (
            select(Stage.id)
            .join(Skill, Skill.id == Stage.skill_id)
            .join(LevelSkill, LevelSkill.skill_id == Skill.id)
            .join(ProfileLevel, ProfileLevel.id == LevelSkill.profile_level_id)
            .join(UserProfile, UserProfile.current_level_id == ProfileLevel.id)
            .where(
                UserProfile.user_id == user_id,
                Stage.id == stage_id,
            )
            .limit(1)
        )

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def delete_by_user_id(self, user_id: int):
        stmt = delete(UserProfile).where(UserProfile.user_id == user_id)
        res = await self._session.execute(stmt)
        return res.rowcount

    async def get_count(self, profile_id):
        stmt = select(func.count(UserProfile.user_id)).where(
            UserProfile.profile_id == profile_id
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


class UserLevelRepository(BaseRepository):
    model = UserLevel

    async def get_current_lvl(self, user_id: int):
        stmt = (
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                joinedload(UserProfile.current_level)
                .load_only(ProfileLevel.id, ProfileLevel.num, ProfileLevel.level_name),
                joinedload(UserProfile.user)
                .selectinload(User.user_skills)
                .load_only(UserSkill.id, UserSkill.is_accepted)
                .selectinload(UserSkill.stages)
                .load_only(UserStage.stage_version_id, UserStage.is_accepted)
                .joinedload(UserStage.stage_version)
                .load_only(StageVersion.stage_id)
            )
        )

        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_level_id(self, user_id: int, level_id: int):
        stmt = select(UserLevel).where(
            UserLevel.profile_level_id == level_id, UserLevel.user_id == user_id
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_level_count(self, levels_id: list[int]):
        stmt = select(func.count(UserLevel.user_id)).where(UserLevel.profile_level_id.in_(levels_id))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_by_user(self, user_id):
        stmt = delete(UserLevel).where(UserLevel.user_id == user_id)
        res = await self._session.execute(stmt)
        return res.rowcount

    async def get_all_by_user(self, user_id: int):
        stmt = select(UserLevel).where(UserLevel.user_id == user_id)
        res = await self._session.execute(stmt)
        return res.scalars().all()
