from enum import StrEnum


class ApiVersion(StrEnum):
    NONE: str = ""
    V1: str = "/api/v1"


class AppVersion(StrEnum):
    BETA: str = "0.1.0-beta.1"
