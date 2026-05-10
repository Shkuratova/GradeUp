from enum import  Enum

class UserRole(str, Enum):
    ADMIN = "Admin"
    SPO = "Specialist"
    SUPERVISOR = "Supervisor"
    EMPLOYEE = "Employee"

class CertificationRole(str, Enum):
    STUDENT = "Аттестуемый"
    EXAMINER = "Аттестующий"
    SUPERVISOR = "Руководитель"
