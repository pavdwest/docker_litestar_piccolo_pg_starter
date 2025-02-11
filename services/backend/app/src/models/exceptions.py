from litestar.exceptions import HTTPException, NotFoundException
from litestar import status_codes
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.base import AppModel
from src.exceptions import AppException


# Monkeypatch
@classmethod
def from_id(cls, id: int, ModelClass: 'type[AppModel]'):
    return cls(f"{ModelClass.humanise()} with id='{id}' not found.")
NotFoundException.from_id = from_id


class ColumnNotFoundException(NotFoundException):
    status_code = status_codes.HTTP_500_INTERNAL_SERVER_ERROR


class ConflictException(HTTPException, AppException):
    """Exception for conflict errors like uniqueness constraints."""

    status_code = status_codes.HTTP_409_CONFLICT
