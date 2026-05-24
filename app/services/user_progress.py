from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import LevelRepository, UserLevelRepository, UserSkillRepository
from schemas.profiles import ProfileStructure, LevelStructure
from schemas.user_progress import ProfileProgress
from services.user_profile import UserProfileService
from services.profile import ProfileService


class UserProgressService:
    def __init__(self, session: AsyncSession):
        self.profile_service = ProfileService(session)
        self.user_profile_service = UserProfileService(session)
        self.level_repository = LevelRepository(session)
        self.user_level_repository = UserLevelRepository(session)
        self.user_skill_repository = UserSkillRepository(session)

    async def get_profile_progress(self, user_id: int):
        user_profile = await self.user_profile_service.get_profile(user_id)
        profile: ProfileStructure = await self.profile_service.get_structure(
            user_profile.profile_id
        )
        user_progress: ProfileProgress = await self.user_profile_service.progress(
            user_id
        )

        user_skill_map = {us.skill_id: us for us in user_progress.skills}
        stage_map = {}
        for us in user_progress.skills:
            for st in us.stages:
                stage_map[st.stage_id] = st
        result_levels = []
        for level in profile.levels:
            result_skills = []
            for skill in level.skill_list:
                user_skill = user_skill_map.get(skill.id)

                result_stages = []
                for stage in skill.stages:
                    user_stage = stage_map.get(stage.id)
                    result_stages.append(
                        {
                            "id": (user_stage.id if user_stage is not None else None),
                            "stage_id": stage.id,
                            "stage_version_id": (
                                user_stage.stage_version_id
                                if user_stage is not None
                                else None
                            ),
                            "confirmation_type": stage.confirmation_type,
                            "is_accepted": (
                                user_stage.is_accepted
                                if user_stage is not None
                                else False
                            ),
                            "comment": (
                                user_stage.comment if user_stage is not None else None
                            ),
                        }
                    )
                result_skills.append(
                    {
                        "id": skill.id,
                        "title": skill.title,
                        "is_accepted": (
                            user_skill.is_accepted if user_skill is not None else False
                        ),
                        "stages": result_stages,
                    }
                )
            result_levels.append(
                {
                    "id": level.id,
                    "num": level.num,
                    "level_name": level.level_name,
                    "skills": result_skills,
                }
            )
        res = {
            "user_id": user_progress.user_id,
            "profile_id": profile.id,
            "title": profile.title,
            "levels": result_levels,
        }
        return res
