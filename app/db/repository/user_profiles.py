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
)
from schemas.skills import SkillStages


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
                Profile.id.label("profile_id"),
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

    async def get_progress(self, user_id: int, profile_id: int):
        level_status_subq = (
            select(UserLevel.profile_level_id, UserLevel.is_closed)
            .where(UserLevel.user_id == user_id)
            .subquery()
        )

        user_progress_subq = (
            select(
                UserLevel.id.label("user_level_id"),
                UserLevel.profile_level_id,
                UserSkill.skill_id,
                Stage.id.label("stage_id"),
                UserStage.is_accepted.label("stage_accepted"),
            )
            .join(UserSkill, UserSkill.user_level_id == UserLevel.id)
            .join(UserStage, UserStage.user_skill_id == UserSkill.id)
            .join(StageVersion, StageVersion.id == UserStage.stage_version_id)
            .join(Stage, Stage.id == StageVersion.stage_id)
            .where(UserLevel.user_id == user_id)
            .subquery()
        )

        query = (
            select(
                ProfileLevel.id.label("profile_level_id"),
                ProfileLevel.num,
                ProfileLevel.level_name,
                level_status_subq.c.is_closed,
                user_progress_subq.c.user_level_id,
                Skill.id.label("skill_id"),
                Skill.title.label("skill_title"),
                Stage.id.label("stage_id"),
                Stage.confirmation_type,
                user_progress_subq.c.stage_accepted,
            )
            .select_from(Profile)
            .join(ProfileLevel, ProfileLevel.profile_id == Profile.id)
            .join(LevelSkill, LevelSkill.profile_level_id == ProfileLevel.id)
            .join(Skill, Skill.id == LevelSkill.skill_id)
            .join(Stage, Stage.skill_id == Skill.id)
            .outerjoin(
                user_progress_subq,
                and_(
                    user_progress_subq.c.profile_level_id == ProfileLevel.id,
                    user_progress_subq.c.skill_id == Skill.id,
                    user_progress_subq.c.stage_id == Stage.id,
                ),
            )
            .outerjoin(
                level_status_subq,
                level_status_subq.c.profile_level_id == ProfileLevel.id,
            )
            .where(Profile.id == profile_id)
            .order_by(ProfileLevel.id, Skill.id, Stage.id)
        )

        result = await self._session.execute(query)
        return result.mappings().all()

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
                    LevelSkill,
                    ~exists(
                        select(1)
                        .select_from(UserSkill)
                        .join(
                            UserLevel,
                            UserLevel.id == UserSkill.user_level_id,
                        )
                        .where(
                            and_(
                                UserSkill.skill_id == LevelSkill.skill_id,
                                UserLevel.user_id == user_id,
                                UserSkill.is_accepted.is_(True),
                            )
                        )
                    ).correlate(LevelSkill),
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

class UserLevelRepository(BaseRepository):
    model = UserLevel

    async def get_current_lvl(self, user_id: int):
        stmt = (
            select(UserLevel)
            .join(
                UserProfile, UserProfile.current_level_id == UserLevel.profile_level_id
            )
            .where(UserProfile.user_id == user_id)
            .where(UserLevel.user_id == user_id)
            .options(
                joinedload(UserLevel.profile_level)
                .selectinload(ProfileLevel.skills)
                .load_only(LevelSkill.skill_id)
            )
        )

        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

        res = await self._session.execute(stmt)
        return res.unique().scalar_one_or_none()


class UserSkillRepository(BaseRepository):
    model = UserSkill

    async def add_skill(self, user_id: int, skill_id: int):
        stmt = (
            insert(UserSkill)
            .from_select(
                ["user_level_id", "skill_id"],
                select(UserLevel.id, literal(skill_id)).where(
                    UserLevel.user_id == user_id
                ),
            )
            .returning(UserSkill)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one()

    async def get_by_user(self, user_id: int, skill_id: int):
        stmt = select(UserSkill).where(
            and_(
                UserSkill.skill_id == skill_id,
                UserSkill.user_level.has(UserLevel.user_id == user_id),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_skill_detail(self, user_id: int, skill_id: int):
        stmt = (
            select(
                Skill.id.label("skill_id"),
                Skill.title,
                Skill.description,
                Skill.literature,
                Stage.id.label("stage_id"),
                Stage.confirmation_type,
                UserStage.id.label("user_stage_id"),
                UserStage.is_accepted,
                UserStage.comment,
                UserStage.updated_at,
            )
            .select_from(Skill)
            .join(Stage, Stage.skill_id == Skill.id)
            .join(StageVersion, StageVersion.stage_id == Stage.id)
            .outerjoin(
                UserSkill,
                UserSkill.skill_id == Skill.id,
            )
            .outerjoin(
                UserLevel,
                and_(
                    UserLevel.id == UserSkill.user_level_id,
                    UserLevel.user_id == user_id,
                ),
            )
            .outerjoin(
                UserStage,
                and_(
                    UserStage.user_skill_id == UserSkill.id,
                    UserStage.stage_version_id == StageVersion.id,
                ),
            )
            .where(Skill.id == skill_id)
        )
        res = await self._session.execute(stmt)
        return res.mappings().all()

    async def get_accepted_count(self, user_level_id: int) -> int:
        stmt = (
            select(func.count(UserSkill.id))
            .join(
                UserLevel,
                UserSkill.user_level_id == UserLevel.id,
            )
            .where(
                UserLevel.id == user_level_id,
                UserSkill.is_accepted.is_(True),
            )
        )

        res = await self._session.execute(stmt)

        return res.scalar_one()


class UserStageRepository(BaseRepository):
    model = UserStage

    async def get_by_version_id(self, user_id: int, stage_version_id: int):
        stmt = (
            select(UserStage)
            .join(UserStage.user_skill)
            .join(UserSkill.user_level)
            .where(
                UserLevel.user_id == user_id,
                UserStage.stage_version_id == stage_version_id,
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_stage_id(self, stage_id: int):
        stmt = (
            select(UserStage)
            .join(UserStage.stage_version)
            .join(StageVersion.stage)
            .where(Stage.id == stage_id)
        )

        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def accepted_count(self, skill_id: int, user_skill_id: int):
        stmt = (
            select(func.count(UserStage.id))
            .join(StageVersion, StageVersion.id == UserStage.stage_version_id)
            .where(
                UserStage.user_skill_id == user_skill_id,
                UserStage.is_accepted.is_(True),
                StageVersion.stage_id.in_(
                    select(Stage.id).where(Stage.skill_id == skill_id)
                ),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
