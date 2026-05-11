from sqlalchemy import select, insert, func
from sqlalchemy.orm import joinedload, contains_eager

from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler
from db.models.skills import Stage, StageVersion, StageQuestion


class StageRepository(BaseRepository):
    model = Stage


    @classmethod
    def last_version_subquery(cls):
        last_versions = (
            select(
                StageVersion.stage_id,
                func.max(StageVersion.version).label("version"),
            )
            .group_by(StageVersion.stage_id)
            .subquery()
        )

        return (
            select(StageVersion)
            .join(
                last_versions,
                (StageVersion.stage_id == last_versions.c.stage_id)
                & (StageVersion.version == last_versions.c.version),
            )
            .subquery()
        )

    @db_exception_handler
    async def get_last_version_by_id(self, stage_id: int):
        last_version = self.last_version_subquery()
        stmt = stmt = (
            select(StageVersion.id, last_version.c.version)
            .where(StageVersion.stage_id == stage_id)
            .join(last_version, (StageVersion.stage_id == last_version.c.stage_id)
                & (StageVersion.version == last_version.c.version),)
        )

        res = await self._session.execute(stmt)
        return res.first()


    @db_exception_handler
    async def get_questions(self, stage_id: int):
        last_version = self.last_version_subquery()

        stmt = (
            select(Stage)
            .where(Stage.id == stage_id)
            .join(last_version, last_version.c.stage_id == Stage.id)
            .join(
                StageVersion,
                (StageVersion.stage_id == Stage.id)
                & (StageVersion.version == last_version.c.version),
            )
            .join(StageQuestion, StageVersion.id == StageQuestion.stage_version_id)
            .options(
                contains_eager(Stage.stage_versions).contains_eager(
                    StageVersion.questions
                )
            )
        )
        res = await self._session.execute(stmt)
        return res.unique().scalar_one_or_none()


class StageVersionRepository(BaseRepository):
    model = StageVersion
    @db_exception_handler
    async def add_new_version(self, stage_id: int):
        stmt = (
            insert(StageVersion)
            .values(
                stage_id=stage_id,
                version=(
                    select(func.coalesce(func.max(StageVersion.version), 0) + 1)
                    .where(StageVersion.stage_id == stage_id)
                    .scalar_subquery()
                ),
            )
            .returning(StageVersion.id, StageVersion.version)
        )
        res = await self._session.execute(stmt)
        return res.first()