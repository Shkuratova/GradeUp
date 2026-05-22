from db import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, text




class User(Base):
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    patronymic: Mapped[str | None]
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete='SET NULL'), nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, server_default=text("1"))
    position: Mapped[str] = mapped_column(nullable=True)

    role: Mapped["Role"] = relationship(back_populates="users")
    department: Mapped["Department"] = relationship(back_populates="users", foreign_keys=[department_id])

    managed_department: Mapped["Department"] = relationship(back_populates="supervisor", foreign_keys="[Department.supervisor_id]",)
    managed_division: Mapped["Division"] = relationship(back_populates="supervisor")

    profile: Mapped["UserProfile"] = relationship(back_populates="user")
    levels: Mapped[list["UserLevel"]] = relationship(back_populates="user")
    meetings: Mapped["MeetingParticipant"] = relationship(back_populates="user")

    user_stages: Mapped[list["UserStage"]] = relationship(back_populates="supervisor")
    events: Mapped[list["Event"]] = relationship(back_populates="actor")