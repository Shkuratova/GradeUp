import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    LevelRepository,
    UserLevelRepository,
    UserSkillRepository,
    UserProfileRepository,
)
from schemas.user_progress import ProfileProgress
from services.users.user_profile import UserProfileService


class UserProgressService:
    def __init__(self, session: AsyncSession):
        self.user_profile_service = UserProfileService(session)
        self.user_profile_repository = UserProfileRepository(session)
        self.level_repository = LevelRepository(session)
        self.user_level_repository = UserLevelRepository(session)
        self.user_skill_repository = UserSkillRepository(session)

    async def get_profile_progress(self, user_id: int):
        user_profile = await self.user_profile_service.get_profile_title(user_id)
        rows = await self.user_profile_repository.get_progress_by_id(user_id=user_id, profile_id=user_profile.profile_id)
        if not len(rows):
            return ProfileProgress.model_validate(user_profile, from_attributes=True)

        levels = defaultdict(
            lambda: {
                "id": None,
                "num": None,
                "level_name": None,
                "is_closed": None,
                "skills": [],
            }
        )

        for row in rows:
            level = levels[row["level_id"]]
            if level["id"] is None:
                level["id"] = row["level_id"]
                level["num"] = row["num"]
                level["level_name"] = row["level_name"]
                level["is_closed"] = row["is_closed"]

            level["skills"].append(
                {
                    "id": row["skill_id"],
                    "title": row["skill_title"],
                    "is_accepted": row["skill_accepted"],
                    "stage_cnt": row["stage_cnt"],
                    "accepted_stages": row["accepted_stages"],
                }
            )

        profile_progress = {
            "profile_id": user_profile.profile_id,
            "user_id": user_id,
            "title": user_profile.title,
            "current_level_id": user_profile.current_level_id,
            "levels": list(levels.values()),
        }

        return ProfileProgress.model_validate(profile_progress)
