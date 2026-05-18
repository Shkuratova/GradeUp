from datetime import datetime

from sqlalchemy import ForeignKey, text, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from db.models.types import CertificationRole, CertificationStatus


class Meeting(Base):
    user_stage_id: Mapped[int] = mapped_column(ForeignKey('user_stages.id', ondelete="CASCADE"))
    status: Mapped[CertificationStatus] = mapped_column(server_default=(CertificationStatus.planned.value))
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("TIMEZONE('utc', now())"))
    duration: Mapped[int]
    location: Mapped[str]
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_stage: Mapped["UserStage"] = relationship(back_populates="meetings")
    participants: Mapped[list["MeetingParticipant"]] = relationship(back_populates="meeting")


class MeetingParticipant(Base):
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role: Mapped[CertificationRole] = mapped_column(default=CertificationRole.student, server_default=CertificationRole.student)

    meeting: Mapped[Meeting] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="meetings")