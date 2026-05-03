from db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, text, UniqueConstraint

from db.models.profiles import ProfileLevelVersion
from db.models.types import ConfirmationTypes

class Category(Base):
    __tablename__ = "categories"
    category_name: Mapped[str]

    skills: Mapped[list["Skill"]] = relationship(secondary="skill_categories", back_populates="categories")



class Skill(Base):
    title: Mapped[str]
    literature: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] =  mapped_column(default=True, server_default=text('true'))

    stages: Mapped[list["Stage"]] = relationship(back_populates="skill")
    # creator: Mapped["User"] = relationship(back_populates="skills_created")
    categories: Mapped[list[Category]] = relationship(back_populates="skills", secondary="skill_categories")

    profile_levels: Mapped[list["LevelSkill"]] = relationship(back_populates="skill")

class SkillCategory(Base):
    __tablename__ = "skill_categories"
    __table_args__ = (UniqueConstraint("skill_id", "category_id"), )

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))

class LevelSkill(Base):
    profile_level_version_id: Mapped[int] = mapped_column(ForeignKey("profile_level_versions.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))


    profile_level_version: Mapped["ProfileLevelVersion"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(back_populates="profile_levels")


class Stage(Base):
    __table_args__ = (UniqueConstraint('skill_id', 'confirmation_type', name='stage_unq_constraint'), )

    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    confirmation_type: Mapped[ConfirmationTypes]
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text('true'))

    skill: Mapped[Skill] = relationship(back_populates="stages")
    stage_versions: Mapped[list[StageVersion]] = relationship(back_populates="stage")

class StageVersion(Base):
    __table_args__ = (UniqueConstraint("stage_id", "version"),)

    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id", ondelete="CASCADE"))
    version: Mapped[int]

    stage: Mapped[Stage] = relationship(back_populates="stage_versions")
    questions: Mapped[list["StageQuestion"]] = relationship(back_populates="stage_version")

class StageQuestion(Base):
    stage_version_id: Mapped[int] = mapped_column(ForeignKey("stage_versions.id", ondelete="CASCADE"))
    num: Mapped[int]
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("stage_version_id", "num", name="question_unq_constraint"), )
    stage_version: Mapped[StageVersion] =relationship(back_populates="questions")
