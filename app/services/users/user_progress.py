import logging
logger = logging.getLogger(__name__)

from collections import defaultdict
from exceptions.common import NotFoundException
from exceptions.user import ForbiddenException

from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    UserSkillRepository,
    UserProfileRepository,
    StageRepository,
    StageVersionRepository,
)
from schemas.user_progress import ProfileProgress, SkillProgresSchema


class UserProgressService:
    def __init__(self, session: AsyncSession):
        self.user_profile_repository = UserProfileRepository(session)
        self.user_skill_repository = UserSkillRepository(session)
        self.stage_repository = StageRepository(session)
        self.stage_version_repository = StageVersionRepository(session)

    async def get_profile_progress(self, user_id: int):
        user_profile = await self.user_profile_repository.get_profile_title(user_id)
        if user_profile is None:
            raise ForbiddenException(f"Пользователю (user_id={user_id}) не назначен профиль")

        rows = await self.user_profile_repository.get_progress_by_id(
            user_id=user_id, profile_id=user_profile.profile_id
        )
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
            "description": user_profile.description,
            "current_level_id": user_profile.current_level_id,
            "levels": list(levels.values()),
        }

        return ProfileProgress.model_validate(profile_progress)

    async def get_skill_progress(
        self, user_id: int, skill_id: int, with_questions: bool = False
    ):
        rows = await self.user_skill_repository.get_skill_progress(user_id, skill_id)

        if not len(rows):
            raise NotFoundException(
                f"Навык пользователя с (user_id ={user_id}, skill_id={skill_id}) не найден."
            )

        res = {
            "user_id": user_id,
            "skill_id": skill_id,
            "title": rows[0]["title"],
            "description": rows[0]["description"],
            "literature": rows[0]["literature"],
            "is_accepted": rows[0]["skill_accepted"],
            "stages": [
                {
                    "stage_id": row["stage_id"],
                    "confirmation_type": row["confirmation_type"],
                    "stage_version_id": row["stage_version_id"],
                    "user_stage_id": row["user_stage_id"],
                    "is_accepted": row["stage_accepted"],
                    "comment": row["comment"],
                    "updated_at": row["updated_at"],
                }
                for row in rows
            ],
        }
        if with_questions:
            for stage in res["stages"]:
                if stage["stage_version_id"] is not None:
                    stage_version = await self.stage_version_repository.get_questions(
                        stage["stage_version_id"]
                    )
                    stage["questions"] = (
                        stage_version.questions if stage_version else None
                    )
                else:
                    last_stage_v = await self.stage_repository.get_questions(stage["stage_id"])
                    stage["questions"] = (
                        last_stage_v.stage_versions[0].questions
                        if last_stage_v.stage_versions
                        else None
                    )

        return SkillProgresSchema.model_validate(res, from_attributes=True)
