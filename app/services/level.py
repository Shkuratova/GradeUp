from services.base import BaseService
from db.repository.profiles import ProfileLevelRepository
from db.repository.skill import SkillRepository, LevelSkillRepository
from schemas.profiles import SLevelAdd, SLevelUpdate, SLevel
from exceptions.common import DataValidationError, NotFoundException


class LevelService(BaseService):
    entity_name = "Уровень"
    repository_factory = ProfileLevelRepository

    async def process_levels(
        self, profile_id: int, levels: list, old_levels: dict = None
    ):
        level_repo = self.repository_factory(self.session)
        level_skill_repo = LevelSkillRepository(self.session)

        old_map = old_levels or {}
        existing_skills = {s.id for lvl in old_map.values() for s in lvl.skills}

        if old_map:
            to_delete = [
                lvl_id
                for lvl_id in old_map
                if lvl_id not in {l.id for l in levels if l.id}
            ]
            if to_delete:
                await level_repo.delete_list(to_delete)
                for lvl_id in to_delete:
                    existing_skills -= {s.id for s in old_map[lvl_id].skills}

        skills_to_add = []
        for lvl in levels:
            skill_ids = set(lvl.skills or [])

            if lvl.id and lvl.id in old_map:
                old_lvl = old_map[lvl.id]
                if lvl.level != old_lvl.level:
                    await level_repo.update_by_id(lvl.id, {"level": lvl.level})

                old_skill_ids = {s.id for s in old_lvl.skills}
                add = skill_ids - old_skill_ids
                remove = old_skill_ids - skill_ids

                if add and (add & existing_skills):
                    raise DataValidationError("Навык может быть привязан только к одному уровню в рамках профиля.")

                if remove:
                    await level_skill_repo.delete_by_skill_ids(lvl.id, list(remove))
                    existing_skills -= remove

                skills_to_add.extend(
                    [{"profile_level_id": lvl.id, "skill_id": s} for s in add]
                )
                existing_skills.update(add)

            else:
                if skill_ids & existing_skills:
                    raise DataValidationError("Навык может быть привязан только к одному уровню в рамках профиля.")

                created = await level_repo.add(
                    {"profile_id": profile_id, "level": lvl.level}
                )
                skills_to_add.extend(
                    [{"profile_level_id": created.id, "skill_id": s} for s in skill_ids]
                )
                existing_skills.update(skill_ids)

        if skills_to_add:
            await level_skill_repo.add_list(skills_to_add)

    async def add_levels_with_skills(self, profile_id: int, levels: list[SLevelAdd]):
        all_skills = set()
        for lvl in levels:
            if lvl.skills:
                if set(lvl.skills) & all_skills:
                    raise DataValidationError("Навык может быть привязан только к одному уровню в рамках профиля.")
                all_skills.update(lvl.skills)

        if all_skills:
            existing = await SkillRepository(self.session).check_list(list(all_skills))
            if missing := all_skills - set(existing):
                raise NotFoundException(f"Навыки {missing} не найдены")

        await self.process_levels(profile_id, levels)

    async def update_levels_with_skills(
        self, profile_id: int, old_levels: list[SLevel], levels: list[SLevelUpdate]
    ):
        await self.process_levels(profile_id, levels, {l.id: l for l in old_levels})
