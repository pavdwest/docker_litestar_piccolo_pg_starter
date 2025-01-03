from litestar.exceptions import HTTPException
from litestar import status_codes

from src.base.exceptions import AppException


class NotFoundException(AppException):
    @classmethod
    def from_id(cls, id: int):
        return cls(f"Item with id='{id}' not found.")

    def http_exception(self):
        raise HTTPException(str(self), status_code=status_codes.HTTP_404_NOT_FOUND)


class TenantNotProvidedForTenantQuery(AppException):
    def __init__(self):
        super().__init__("Tenant not provided for tenant query.")
