from db import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, text, UniqueConstraint


class Role(Base):
    role_name: Mapped[str]
    users: Mapped[list["User"]] = relationship(back_populates="role")


class Department(Base):
    department_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    division_id: Mapped[int | None] = mapped_column(ForeignKey("divisions.id", ondelete="SET NULL"), )
    description: Mapped[str | None]
    supervisor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True)

    division: Mapped["Division"] = relationship(back_populates="departments")
    users: Mapped[list["User"]] = relationship(
        back_populates="department",
        foreign_keys="[User.department_id]"
    )
    supervisor: Mapped["User"] = relationship(back_populates="managed_department", foreign_keys=[supervisor_id])
    profiles: Mapped[list["Profile"]] = relationship(secondary="department_profiles", back_populates="departments")

class Division(Base):
    division_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    departments: Mapped[list["Department"]] = relationship(back_populates="division")
    description: Mapped[str | None]
    supervisor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True)
    supervisor: Mapped["User"] = relationship(back_populates="managed_division", foreign_keys=[supervisor_id])

class DepartmentProfile(Base):
    __table_args__ = (UniqueConstraint("department_id", "profile_id"), )
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))

