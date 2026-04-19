from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Text
from db.database import Base


class Profile(Base):
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    levels: Mapped[list["ProfileLevel"]] = relationship(back_populates="profile")
    users: Mapped[list["User"]] = relationship(back_populates="profile")


class ProfileLevel(Base):
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE")
    )
    level: Mapped[str] = mapped_column(nullable=False)

    profile: Mapped["Profile"] = relationship(back_populates="levels")
    skills: Mapped[list["LevelSkill"]] = relationship(
        back_populates="profile_level", cascade="all, delete-orphan"
    )
