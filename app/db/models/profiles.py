from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Text, text, UniqueConstraint
from db.database import Base
from db.models.user_profiles import UserProfile
from db.models.user_profiles import UserSkill


class Profile(Base):
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))

    departments: Mapped["Department"] = relationship(secondary="department_profiles", back_populates="profiles")
    levels: Mapped[list["ProfileLevel"]] = relationship(back_populates="profile", order_by="ProfileLevel.num")
    user_profiles: Mapped[list["UserProfile"]] = relationship(back_populates="profile")


class ProfileLevel(Base):
    __table_args__ = (UniqueConstraint("profile_id", "level_name"),
                      UniqueConstraint("profile_id", "num"), )
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE")
    )
    num: Mapped[int] = mapped_column(default=1, server_default=text('1'))
    level_name: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text('true'))

    profile: Mapped["Profile"] = relationship(back_populates="levels")
    skills: Mapped[list["LevelSkill"]] = relationship(back_populates="profile_level")
    skill_list: Mapped[list["Skill"]] = relationship(back_populates="profile_level", secondary="level_skills")
    user_profiles: Mapped["UserProfile"] = relationship(back_populates="current_level")
    user_levels: Mapped["UserLevel"] = relationship(back_populates="profile_level")
    user_skills: Mapped[list["UserSkill"]] = relationship(back_populates="profile_level")