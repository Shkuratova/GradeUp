from app.db import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, text


class Department(Base):
    department_name: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="department")

class Position(Base):
    position: Mapped[str]
    
    users: Mapped[list["User"]] = relationship(back_populates="position")
    profiles: Mapped[list["Profile"]] = relationship(back_populates="position")

class Role(Base):
    role_name: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="role")

class User(Base):
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str | None] 
    last_name: Mapped[str | None] 
    patronymic: Mapped[str | None] 
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"), nullable=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, server_default=text("1"))
    
    position: Mapped["Position"] = relationship( back_populates="users")
    department: Mapped["Department"] = relationship( back_populates="users")
    role: Mapped["Role"] = relationship( back_populates="users")

    skills_created: Mapped[list["Skill"]] = relationship(back_populates="creator")