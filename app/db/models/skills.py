from db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, text, UniqueConstraint
from enum import Enum


class ConfirmationTypes(str, Enum):
    certification = "Аттестация"
    performance_review = "Performance review"
    practice = "Практическое задание"



class Skill(Base):
    title: Mapped[str]
    literature: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    creator: Mapped["User"] = relationship(back_populates="skills_created")
    stages: Mapped[list["SkillStage"]] = relationship(back_populates="skill")


class SkillStage(Base):
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    confirmation_type: Mapped[ConfirmationTypes]
    creator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    __table_args__ = (UniqueConstraint('skill_id', 'confirmation_type', name='stage_unq_constraint'), )
    skill: Mapped[Skill] = relationship(back_populates="stages")
    questions: Mapped[list[StageQuestion]] = relationship(back_populates="stage")

class LevelSkill(Base):
    profile_level_id: Mapped[int] = mapped_column(ForeignKey("profile_levels.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))


class StageQuestion(Base):
    num: Mapped[int]
    stage_id: Mapped[int] = mapped_column(ForeignKey("skill_stages.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("stage_id", "num", name="question_unq_constraint"), )
    stage: Mapped[SkillStage] =relationship(back_populates="questions")
