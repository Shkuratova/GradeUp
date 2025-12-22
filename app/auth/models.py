from app.db import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, text


class Department(Base):
    department_name: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="department")

class Position(Base):
    position: Mapped[str]
    
    users: Mapped[list["User"]] = relationship(back_populates="position")


class Role(Base):
    role_name: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="role")

class User(Base):
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str] 
    last_name: Mapped[str] 
    patronymic: Mapped[str] 
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, server_default=text("1"))
    
    position: Mapped["Position"] = relationship( back_populates="users")
    department: Mapped["Department"] = relationship( back_populates="users")
    role: Mapped["Role"] = relationship( back_populates="users")