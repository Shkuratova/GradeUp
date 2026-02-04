from app.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text
from datetime import datetime
from enum import Enum


class UserProfiles(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))


class UserCertification(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user_id"))
    certification_id: Mapped[int] = mapped_column(ForeignKey("certifications.id")) #FK1
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    certification_version: Mapped[int] # FK1
    status: Mapped[str]
    is_accepted: Mapped[bool] = mapped_column(server_default=text('false'))
    date_started: Mapped[datetime]


class CertificationRole(str, Enum):
    student = "Аттестуемый"
    examiner = "Аттестующий"
    supervisor = "Руководитель" # для отметки perfomance review и практических заданий
    # expert

class CertificationParticipant(Base):
    user_certification_id: Mapped[int] = mapped_column("user_certifications.id")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_role: Mapped[CertificationRole] = mapped_column()


class UserAnswer(Base):
    user_id: Mapped[int] = mapped_column("users.id")
    question_id: Mapped[int] = mapped_column("certification_questions.id")
    is_accepted: Mapped[bool]  = mapped_column(server_default=text('false')) # или Enum (зачтено, не зачтено, не отвечал)
