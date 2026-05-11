from enum import Enum


class ConfirmationTypes(str, Enum):
    certification = "Аттестация"
    performance_review = "Performance review"
    practice = "Практическое задание"

class CertificationRole(str, Enum):
    student = "Аттестуемый"
    examiner = "Аттестующий"
    supervisor = "Руководитель"


class CertificationStatus(str, Enum):
    planned = "planned"
    completed = "completed"