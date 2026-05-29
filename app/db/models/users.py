from db import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, text




class User(Base):
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    patronymic: Mapped[str | None]
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, server_default=text("1"))
    position: Mapped[str] = mapped_column(nullable=True)

    role: Mapped["Role"] = relationship(back_populates="users")
    department: Mapped["Department"] = relationship(secondary="department_users", uselist=False)
    managed_division: Mapped["Division"] = relationship(back_populates="supervisor")
    department_role: Mapped["DepartmentUser"] = relationship(back_populates="user", uselist=False)
    profile: Mapped["UserProfile"] = relationship(back_populates="user")
    levels: Mapped[list["UserLevel"]] = relationship(back_populates="user")
    meetings: Mapped["MeetingParticipant"] = relationship(back_populates="user")

    user_stages: Mapped[list["UserStage"]] = relationship(back_populates="supervisor")
    events: Mapped[list["Event"]] = relationship(back_populates="actor")