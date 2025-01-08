from litestar.exceptions import HTTPException
from litestar import status_codes

from src.exceptions import AppException


class NotFoundException(AppException):
    @classmethod
    def from_id(cls, id: int):
        return cls(f"Item with id='{id}' not found.")

    def http_exception(self):
        raise HTTPException(str(self), status_code=status_codes.HTTP_404_NOT_FOUND)


class UniquenessException(AppException):
    def http_exception(self):
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=str(self),
        )


class TenantNotProvidedForTenantQuery(AppException):
    def __init__(self):
        super().__init__("Tenant not provided for tenant query.")
