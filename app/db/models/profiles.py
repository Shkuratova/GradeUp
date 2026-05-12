from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Text, text, UniqueConstraint
from db.database import Base
from db.models.user_profiles import UserProfile


class Profile(Base):
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=True)

    departments: Mapped["Department"] = relationship(secondary="department_profiles", back_populates="profiles")
    levels: Mapped[list["ProfileLevel"]] = relationship(back_populates="profile", order_by="ProfileLevel.num")
    user_profiles: Mapped[list["UserProfile"]] = relationship(back_populates="profile")


class ProfileLevel(Base):
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE")
    )
    num: Mapped[int] = mapped_column(default=1, server_default=text('1'))
    level_name: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text('true'))

    profile: Mapped["Profile"] = relationship(back_populates="levels")
    versions: Mapped[list["ProfileLevelVersion"]] = relationship(back_populates="profile_level")

class ProfileLevelVersion(Base):
    profile_level_id: Mapped[int] = mapped_column(ForeignKey("profile_levels.id"))
    version: Mapped[int] = mapped_column(server_default=text('1'))

    profile_level: Mapped[ProfileLevel] = relationship(back_populates="versions")
    skills: Mapped[list["LevelSkill"]] = relationship(back_populates="profile_level_version")

    __table_args__ = (UniqueConstraint("profile_level_id", "version"),)

