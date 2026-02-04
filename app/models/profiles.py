from app.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, text
from enum import Enum


class Position(Base):
    position: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="position")
    profiles: Mapped[list["Profile"]] = relationship(back_populates="position")



class Profile(Base):
    position_level: Mapped[str]  # or Enum in class Position
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"))

    position: Mapped["Position"] = relationship(back_populates="profiles")

## MtM?
class Category(Base):
    __tablename__ = "categories"

    category_name: Mapped[str]


class Skill(Base):
    title: Mapped[str]
    literature: Mapped[str | None] = mapped_column(Text)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    creator: Mapped["User"] = relationship(back_populates="skills_created")
    stages: Mapped[list["Certification"]] = relationship(back_populates="skill")

class ProfileSkill(Base):
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))


class ConfirmationTypes(str, Enum):
    certification = "Аттестация"
    performance_review = "Performance review"
    practice = "Практическое задание"


class Certification(Base):
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    certification_type: Mapped[ConfirmationTypes]
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(server_default=text("1"))

    skill: Mapped["Skill"] = relationship(back_populates="stages")

class CertificationQuestion(Base):
    num: Mapped[int]
    certification_id: Mapped[int] = mapped_column(ForeignKey("certifications.id"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    certification_version: Mapped[int] = mapped_column(server_default=text("1"))
    creator_id: Mapped[int] = ForeignKey("users.id")
