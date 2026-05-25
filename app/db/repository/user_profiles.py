from sqlalchemy import select, func, and_, exists, delete
from sqlalchemy.orm import joinedload, with_loader_criteria, aliased

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
    StageVersion,
    UserSkill,
    Role,
    Division,
)
from db.repository import BaseRepository
from db.repository.decorators import db_exception_handler


class UserProfileRepository(BaseRepository):
    model = UserProfile

    @db_exception_handler
    async def get_all_with_progress(self, filter_dict: dict):

        profile_progress = (
            select(
                UserProfile.user_id,
                UserProfile.profile_id,
                func.count(ProfileLevel.id).label("level_cnt"),
                func.count(UserLevel.id).label("closed_levels_cnt"),
            )
            .join(ProfileLevel, ProfileLevel.profile_id == UserProfile.profile_id)
            .outerjoin(
                UserLevel,
                and_(
                    UserLevel.profile_level_id == ProfileLevel.id,
                    UserLevel.is_closed.is_(True),
                ),
            )
            .group_by(UserProfile.user_id, UserProfile.profile_id)
            .cte("profile_progress")
        )
        current_skills = (
            select(
                UserProfile.user_id,
                UserProfile.profile_id,
                UserProfile.current_level_id.label("profile_level_id"),
                func.count(LevelSkill.skill_id).label("skill_cnt"),
                func.count(UserSkill.skill_id).label("accepted_cnt"),
            )
            .join(
                LevelSkill, LevelSkill.profile_level_id == UserProfile.current_level_id
            )
            .outerjoin(
                UserSkill,
                and_(
                    UserSkill.skill_id == LevelSkill.skill_id,
                    UserSkill.is_accepted.is_(True),
                ),
            )
            .group_by(
                UserProfile.user_id,
                UserProfile.profile_id,
                UserProfile.current_level_id,
            )
            .cte("current_skills")
        )

        user_profile_info = (
            select(
                Profile.title,
                current_skills.c.profile_id,
                current_skills.c.user_id,
                current_skills.c.profile_level_id,
                ProfileLevel.level_name,
                profile_progress.c.level_cnt,
                profile_progress.c.closed_levels_cnt,
                current_skills.c.skill_cnt,
                current_skills.c.accepted_cnt,
            )
            .join(Profile, Profile.id == current_skills.c.profile_id)
            .join(ProfileLevel, ProfileLevel.id == current_skills.c.profile_level_id)
            .join(
                profile_progress,
                and_(
                    profile_progress.c.user_id == current_skills.c.user_id,
                    profile_progress.c.profile_id == current_skills.c.profile_id,
                ),
            )
        ).cte("user_profile_info")

        managed_department = aliased(Department)
        user_info = (
            select(
                User.id,
                User.first_name,
                User.last_name,
                User.patronymic,
                User.position,
                User.email,
                Department.id.label("department_id"),
                Department.department_name,
                managed_department.id.label("managed_department_id"),
                managed_department.department_name.label("managed_department_name"),
                Division.id.label("managed_division_id"),
                Division.division_name.label("managed_division_name"),
                Role.id.label("role_id"),
                Role.role_name,
            )
            .outerjoin(Department, Department.id == User.department_id)
            .outerjoin(managed_department, managed_department.supervisor_id == User.id)
            .outerjoin(Division, Division.supervisor_id == User.id)
            .join(Role, Role.id == User.role_id)
        )
        departments_id = filter_dict.pop("departments_id", None)
        if departments_id:
            user_info = user_info.where(Department.id.in_(departments_id))
        user_info = user_info.cte("user_info")

        stmt = select(
            user_info.c.id,
            user_info.c.first_name,
            user_info.c.last_name,
            user_info.c.patronymic,
            user_info.c.email,
            user_info.c.position,
            user_info.c.role_id,
            user_info.c.role_name,
            user_info.c.department_id,
            user_info.c.department_name,
            user_info.c.managed_department_id,
            user_info.c.managed_department_name,
            user_info.c.managed_division_id,
            user_info.c.managed_division_name,
            user_profile_info.c.profile_id,
            user_profile_info.c.title,
            user_profile_info.c.level_name,
            user_profile_info.c.level_cnt,
            user_profile_info.c.closed_levels_cnt,
            user_profile_info.c.skill_cnt,
            user_profile_info.c.accepted_cnt,
        ).outerjoin(user_profile_info, user_profile_info.c.user_id == user_info.c.id)

        res = await self._session.execute(stmt)
        return res.mappings().all()

    @db_exception_handler
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

    @db_exception_handler
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

    @db_exception_handler
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
            )
        )

        res = await self._session.execute(stmt)

        return res.scalar_one_or_none()

    @db_exception_handler
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

    @db_exception_handler
    async def delete_by_user_id(self, user_id: int):
        stmt = delete(UserProfile).where(UserProfile.user_id == user_id)
        res = await self._session.execute(stmt)
        return res.rowcount

    @db_exception_handler
    async def get_count(self, profile_id):
        stmt = select(func.count(UserProfile.user_id)).where(
            UserProfile.profile_id == profile_id
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


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
                joinedload(UserProfile.user)
                .selectinload(User.user_skills)
                .load_only(UserSkill.id, UserSkill.is_accepted)
                .selectinload(UserSkill.stages)
                .load_only(UserStage.stage_version_id, UserStage.is_accepted)
                .joinedload(UserStage.stage_version)
                .load_only(StageVersion.stage_id),
            )
        )

        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_by_level_id(self, user_id: int, level_id: int):
        stmt = select(UserLevel).where(
            UserLevel.profile_level_id == level_id, UserLevel.user_id == user_id
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_level_count(self, levels_id: list[int]):
        stmt = select(func.count(UserLevel.user_id)).where(
            UserLevel.profile_level_id.in_(levels_id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def delete_by_user(self, user_id):
        stmt = delete(UserLevel).where(UserLevel.user_id == user_id)
        res = await self._session.execute(stmt)
        return res.rowcount

    @db_exception_handler
    async def get_all_by_user(self, user_id: int):
        stmt = select(UserLevel).where(UserLevel.user_id == user_id)
        res = await self._session.execute(stmt)
        return res.scalars().all()
