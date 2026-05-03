from db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, text, func, TIMESTAMP
from datetime import datetime
from db.models.types import CertificationRole


class UserLevel(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    profile_level_version_id: Mapped[int] = mapped_column(ForeignKey("profile_level_versions.id"))
    is_closed: Mapped[bool] = mapped_column(default=False, server_default=text('false'))

    user: Mapped["User"] = relationship(back_populates="levels")
    skills: Mapped[list["UserSkill"]] = relationship(back_populates="user_level")


class UserSkill(Base):
    user_level_id: Mapped[int] = mapped_column(ForeignKey("user_levels.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    is_accepted: Mapped[bool] = mapped_column(default=False, server_default=text("false"))

    user_level: Mapped[UserLevel]  = relationship(back_populates="skills")
    stages: Mapped[list["UserStage"]] = relationship(back_populates="user_skill")

class UserStage(Base):
    user_skill_id: Mapped[int] = mapped_column(ForeignKey("user_skills.id"))
    stage_version_id: Mapped[int] = mapped_column(ForeignKey("stage_versions.id")) #FK1
    status: Mapped[str]

    user_skill: Mapped[UserSkill] = relationship(back_populates="stages")
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="user_stage")
    answers: Mapped[list["UserAnswer"]] = relationship(back_populates="user_stage")

class UserAnswer(Base):
    user_stage_id: Mapped[int] = mapped_column(ForeignKey("user_stages.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("stage_questions.id"))
    user_answer: Mapped[str]
    is_accepted: Mapped[bool]  = mapped_column(default=False, server_default=text('false')) # или Enum (зачтено, не зачтено, не отвечал)

    user_stage: Mapped[UserStage] = relationship(back_populates="answers")


class Meeting(Base):
    user_stage_id: Mapped[int] = mapped_column(ForeignKey("user_stages.id"))
    status: Mapped[str]
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    duration: Mapped[int]
    location: Mapped[str]
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user_stage: Mapped[UserStage] = relationship(back_populates="meetings")
    participants: Mapped[list["MeetingParticipant"]] = relationship(back_populates="meeting")


class MeetingParticipant(Base):
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role: Mapped[CertificationRole] = mapped_column(default=CertificationRole.student, server_default=CertificationRole.student)

    meeting: Mapped[Meeting] = relationship(back_populates="participants")



