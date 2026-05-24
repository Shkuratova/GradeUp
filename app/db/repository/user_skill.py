from sqlalchemy import select, insert, literal, and_, func, not_, exists
from sqlalchemy.orm import selectinload, joinedload

from db.models import Skill, Stage, ProfileLevel, StageQuestion
from db.models.skills import StageVersion, LevelSkill
from db.models.user_profiles import UserSkill, UserLevel, UserStage, UserProfile
from db.repository import BaseRepository


class UserSkillRepository(BaseRepository):
    model = UserSkill

    async def get_by_user(self, user_id: int, skill_id: int):
        stmt = select(UserSkill).where(
            and_(
                UserSkill.skill_id == skill_id,
                UserSkill.user_id == user_id,
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

    async def get_skill_detail_questions(self, user_id: int, skill_id: int):
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
                StageQuestion.num,
                StageQuestion.question,
                StageQuestion.answer,
            )
            .select_from(Skill)
            # skill → stage
            .join(Stage, Stage.skill_id == Skill.id)
            # фиксируем ОДНУ версию stage (иначе дубли вопросов)
            .join(StageVersion, StageVersion.stage_id == Stage.id)
            # вопросы
            .join(StageQuestion, StageQuestion.stage_version_id == StageVersion.id)
            # user skill (обязательно фильтр по user_id)
            .outerjoin(
                UserSkill,
                and_(
                    UserSkill.skill_id == Skill.id,
                    UserSkill.user_id == user_id,
                ),
            )
            # user stage (тоже строго по user)
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

    async def get_accepted_count(self, user_id: int, profile_level_id: int) -> int:
        stmt = (
            select(func.count(UserSkill.id))
            .where(
                UserSkill.user_id == user_id,
                UserSkill.profile_level_id == profile_level_id,
                UserSkill.is_accepted.is_(True),
            )
        )

        res = await self._session.execute(stmt)

        return res.scalar_one()

    async def get_progress_by_level(self, user_id: int, profile_level_id: int):
        stage_exists = (
            select(1)
            .select_from(UserSkill)
            .join(UserStage, UserStage.user_skill_id == UserSkill.id)
            .join(StageVersion, StageVersion.id == UserStage.stage_version_id)
            .where(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == Skill.id,
                StageVersion.stage_id == Stage.id,
            )
        )

        skill_exists = (
            select(1)
            .select_from(UserSkill)
            .where(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == Skill.id,
                UserSkill.profile_level_id == ProfileLevel.id,
                UserSkill.is_accepted.is_(True),
            )
        )
        stmt = (
            select(
                ProfileLevel.id.label("profile_level_id"),
                ProfileLevel.level_name,
                Skill.id.label("skill_id"),
                Skill.title,
                Stage.id.label("stage_id"),
                Stage.confirmation_type,
            )
            .join(LevelSkill, LevelSkill.profile_level_id == ProfileLevel.id)
            .join(Skill, Skill.id == LevelSkill.skill_id)
            .join(Stage, Stage.skill_id == Skill.id)
            .where(
                ProfileLevel.id == profile_level_id,
                not_(exists(skill_exists)),
                not_(exists(stage_exists)),
            )
        )
        res = await self._session.execute(stmt)
        return res.mappings().all()

    async def get_count_by_skill(self, skill_id):
        stmt = select(func.count(UserSkill.user_id)).where(UserSkill.skill_id == skill_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
