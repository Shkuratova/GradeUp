from sqlalchemy import ForeignKey, UniqueConstraint, Enum, Index, text, and_
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db import Base
from db.models import User
from db.models.types import DepartmentRole


class Role(Base):
    role_name: Mapped[str]
    users: Mapped[list["User"]] = relationship(back_populates="role")


class Department(Base):
    department_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    division_id: Mapped[int | None] = mapped_column(ForeignKey("divisions.id", ondelete="SET NULL"), )
    description: Mapped[str | None]
    # supervisor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True)

    division: Mapped["Division"] = relationship(back_populates="departments")
    # users: Mapped[list["User"]] = relationship(
    #     back_populates="department",
    #     foreign_keys="[User.department_id]"
    # )
    users: Mapped[list["User"]] = relationship(secondary="department_users")
    department_users: Mapped[list["DepartmentUser"]] = relationship(back_populates="department")
    # supervisor: Mapped["User"] = relationship(back_populates="managed_department", foreign_keys=[supervisor_id])
    profiles: Mapped[list["Profile"]] = relationship(secondary="department_profiles", back_populates="departments")
    supervisor: Mapped["User"] = relationship(
        secondary="department_users",
        primaryjoin=lambda: Department.id == DepartmentUser.department_id,
        secondaryjoin=lambda: and_(
            User.id == DepartmentUser.user_id,
            DepartmentUser.role == DepartmentRole.SUPERVISOR
        ),
        uselist=False,
        viewonly=True
    )

class DepartmentUser(Base):
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    role: Mapped[DepartmentRole]

    department: Mapped[Department] = relationship(back_populates="department_users")
    user: Mapped["User"] = relationship(back_populates="department_role")

    __table_args__ = (
        Index(
            "unq_department_supervisor",
            "department_id",
            unique=True,
            postgresql_where=text("role = 'SUPERVISOR'")
        ),
        Index(
            "department_user_idx",
            "department_id",
            "user_id"
        ),
    )


class Division(Base):
    division_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    departments: Mapped[list["Department"]] = relationship(back_populates="division")
    description: Mapped[str | None]
    supervisor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True)
    supervisor: Mapped["User"] = relationship(back_populates="managed_division", foreign_keys=[supervisor_id])

class DepartmentProfile(Base):
    __table_args__ = (UniqueConstraint("department_id", "profile_id"), )
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"))
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"))

