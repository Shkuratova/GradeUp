from app.models import (
    Category,
    Profile,
    ProfileSkill,
    Skill,
    Certification,
    CertificationQuestion,
)
from pydantic import BaseModel
from app.db import BaseDAO
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.models import User

class ProfileDAO(BaseDAO):
    model = Profile

    async def get_profiles_with_positions(self, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        stmt = (
            select(Profile.title, func.count(Certification.skill_id))
            .options(joinedload(Profile.position))
            .filter_by(**filter_dict)
        )
        try:
            res = await self._session.execute(stmt)
            rows = res.scalars().all()
            return rows
        except SQLAlchemyError as e:
            print(e)
            raise


class SkillDAO(BaseDAO):
    model = Skill

    async def get_skills_with_full_info(self, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_none=True) if filters else {}
        subq = (
            select(
                Certification.skill_id,
                func.count(Certification.skill_id).label("num_stages"))
            .group_by(Certification.skill_id)
        ).subquery()
        stmt = (
        select(
            Skill.title,
            func.concat(User.last_name, " ", User.first_name, " ", User.patronymic).label("creator"),
            Skill.created_at,
            func.coalesce(subq.c.num_stages, 0).label("num_stages")
            )
            .join_from(Skill, subq, isouter=True)
            .join(User, isouter=True)
            .filter_by(**filter_dict)
        )
        try:
            res = await self._session.execute(stmt)
            rows = res.all()
            return rows
        except SQLAlchemyError as e:
            print(e)
            raise


class QuestionDAO(BaseDAO):
    model = CertificationQuestion


class CategoryDAO(BaseDAO):
    model = Category
