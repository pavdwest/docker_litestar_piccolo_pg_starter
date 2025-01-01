from typing import Any, Optional
from enum import StrEnum
from functools import lru_cache
from pydantic import computed_field

from src.base.dtos import AppDTO


class DatabaseBind(AppDTO):
    class DatabaseDriver(StrEnum):
        ASYNC = 'postgresql+asyncpg'
        SYNC  = 'postgresql+psycopg2'

    host: str
    name: str
    username: str
    password: str
    port: Optional[str | int] = 5432

    @computed_field
    @property
    def piccolo_config(self) -> dict[str, Any]:
        return {
            "database": self.name,
            "user": self.username,
            "password": self.password,
            "host": self.host,
            "port": self.port,
        }

    @computed_field
    @property
    def url_sync(self) -> str:
        return f"{self.DatabaseDriver.SYNC.value}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

    @computed_field
    @property
    def url_async(self) -> str:
        return f"{self.DatabaseDriver.ASYNC.value}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
