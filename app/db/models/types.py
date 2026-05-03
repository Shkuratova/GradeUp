from enum import Enum

class ConfirmationTypes(str, Enum):
    certification = "Аттестация"
    performance_review = "Performance review"
    practice = "Практическое задание"

class CertificationRole(str, Enum):
    student = "student"
    examiner = "examiner"
    supervisor = "supervisor"