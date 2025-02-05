from enum import StrEnum


class UserRole(StrEnum):
    admin = "admin"
    user = "user"
    executor = "executor"

class AppealStatus(StrEnum):
    accepted = "accepted"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"
    rejected = "rejected"

class AppealResponsibilityArea(StrEnum):
    housing = "housing"
    road = "road"
    administration = "administration"
    law_enforcement = "law_enforcement"
    other = "other"

class TokenType(StrEnum):
    access = "acc"
    refresh = "ref"
