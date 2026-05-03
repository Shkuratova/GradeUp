from db import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, text


class Role(Base):
    role_name: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="role")


class Department(Base):
    department_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="department")


class User(Base):
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    patronymic: Mapped[str | None]
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete='SET NULL'), nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, server_default=text("1"))
    position: Mapped[str] = mapped_column(nullable=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)

    department: Mapped["Department"] = relationship(back_populates="users")
    role: Mapped["Role"] = relationship(back_populates="users")
    profile: Mapped["Profile"] = relationship(back_populates="users")
    levels: Mapped[list["UserLevel"]] = relationship(back_populates="user")
    # skills_created: Mapped[list["Skill"]] = relationship(back_populates="creator")
