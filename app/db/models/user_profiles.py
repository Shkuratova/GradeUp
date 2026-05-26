from sqlalchemy import ForeignKey, text, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class UserProfile(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    current_level_id: Mapped[int] = mapped_column(ForeignKey("profile_levels.id"))

    user: Mapped["User"] = relationship(back_populates="profile")
    profile: Mapped["Profile"] = relationship(back_populates="user_profiles")
    current_level: Mapped["ProfileLevel"] = relationship(back_populates="user_profiles")

class UserLevel(Base):
    __table_args__ = (UniqueConstraint('user_id', 'profile_level_id'), )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    profile_level_id: Mapped[int] = mapped_column(ForeignKey("profile_levels.id"))
    is_closed: Mapped[bool] = mapped_column(default=False, server_default=text('false'))

    user: Mapped["User"] = relationship(back_populates="levels")
    profile_level: Mapped["ProfileLevel"] = relationship(back_populates="user_levels")


class UserSkill(Base):
    __table_args__ = (UniqueConstraint('user_id', 'skill_id'), )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    profile_level_id: Mapped[int] = mapped_column(ForeignKey("profile_levels.id", ondelete="SET NULL"), nullable=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    is_accepted: Mapped[bool] = mapped_column(default=False, server_default=text("false"))


    profile_level: Mapped["ProfileLevel"] = relationship(back_populates="user_skills")
    stages: Mapped[list["UserStage"]] = relationship(back_populates="user_skill")


class UserStage(Base):
    __table_args__ = (UniqueConstraint('user_skill_id', 'stage_version_id'), )
    user_skill_id: Mapped[int] = mapped_column(ForeignKey("user_skills.id"))
    stage_version_id: Mapped[int] = mapped_column(ForeignKey("stage_versions.id"))
    is_accepted: Mapped[bool] = mapped_column(default=False, server_default=text('false'))
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    user_skill: Mapped[UserSkill] = relationship(back_populates="stages")

    stage_version: Mapped["StageVersion"] = relationship()

    meetings: Mapped[list["Meeting"]] = relationship(back_populates="user_stage")

    supervisor: Mapped["User"] = relationship(back_populates="user_stages")
    stage: Mapped["Stage"] = relationship(
        "Stage",
        secondary="stage_versions",
        primaryjoin="UserStage.stage_version_id == StageVersion.id",
        secondaryjoin="StageVersion.stage_id == Stage.id",
        viewonly=True,
    )
    skill: Mapped["Skill"] = relationship(
            "Skill",
            secondary="user_skills",
            primaryjoin="UserStage.user_skill_id == UserSkill.id",
            secondaryjoin="UserSkill.skill_id == Skill.id",
            viewonly=True,
        )
