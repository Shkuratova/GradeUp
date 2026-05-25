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

class EventType(str, Enum):
    EVALUATE = "EVALUATE"  # Оценка этапа
    GRADEUP = "GRADEUP" # Повышение уровня
    SCHEDULE_MEETING = "SCHEDULE_MEETING" # Назначение встречи
    MEETING_CHANGED = "MEETING_CHANGED" # Изменение встречи
    REGISTRATION = "REGISTRATION" # Регистрация
    SET_PROFILE = "SET_PROFILE" # Назначение профиля
    SET_DEPARTMENT_SUPERVISOR = "SET_DEPARTMENT_SUPERVISOR" # Назначение руководителя отдела
    SET_DIVISION_SUPERVISOR = "SET_DIVISION_SUPERVISOR" # Назначение руководителя направления
    REMOVE_DEPARTMENT_SUPERVISOR = "REMOVE_DEPARTMENT_SUPERVISOR" # Открепление руководителя от отдела
    REMOVE_DIVISION_SUPERVISOR = "REMOVE_DIVISION_SUPERVISOR" # Открепление руководителя от направления
    ROLE_CHANGED = "ROLE_CHANGED" # Изменение роли пользователя

class TargetType(str, Enum):
    USER = "USER"
    DEPARTMENT = "DEPARTMENT"
    DIVISION = "DIVISION"
    USER_STAGE = "USER_STAGE"
    USER_PROFILE = "USER_PROFILE"
    MEETING = "MEETING"
