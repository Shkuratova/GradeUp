from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from db.database import Base


class Profile(Base):
    position: Mapped[str] = mapped_column(unique=True)
    levels: Mapped[list["Level"]] = relationship(secondary="profile_levels", back_populates="profiles")


class Level(Base):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    profiles: Mapped[list["Profile"]] = relationship(secondary="profile_levels", back_populates="levels")

class ProfileLevel(Base):
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"))
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id", ondelete="CASCADE"))


    __table_args__ = (
        UniqueConstraint("profile_id", "level_id", name="unq_profile_level"),
    )

