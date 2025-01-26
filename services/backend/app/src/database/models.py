from typing import Any, Optional
from enum import StrEnum

from src.dtos import AppDTO


class DatabaseBind(AppDTO):
    class DatabaseDriver(StrEnum):
        ASYNC = 'postgresql+asyncpg'
        SYNC  = 'postgresql+psycopg2'

    host: str
    name: str
    username: str
    password: str
    port: Optional[str | int] = 5432

    @property
    def piccolo_config(self) -> dict[str, Any]:
        return {
            "database": self.name,
            "user": self.username,
            "password": self.password,
            "host": self.host,
            "port": self.port,
        }

    @classmethod
    def connection_url(cls, host: str, name: str, username: str, password: str, sync: bool = False, port: Optional[str | int] = 5432) -> str:
        return f"{cls.DatabaseDriver.SYNC if sync else cls.DatabaseDriver.ASYNC}://{username}:{password}@{host}:{port}/{name}"

    @property
    def url_sync(self) -> str:
        return self.connection_url(self.host, self.name, self.username, self.password, sync=True, port=self.port)

    @property
    def url_async(self) -> str:
        return self.connection_url(self.host, self.name, self.username, self.password, sync=False, port=self.port)
