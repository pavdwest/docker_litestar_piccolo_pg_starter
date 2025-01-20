from datetime import datetime
from typing import Annotated
from functools import lru_cache

from msgspec import Struct, Meta, structs


StringShort = Annotated[str, Meta(max_length=256)]
StringLong = Annotated[str, Meta(max_length=4096)]
IntPositive = Annotated[int, Meta(gt=0)]
IntNonNegative = Annotated[int, Meta(ge=0)]


# Abstract
class AppDTO(Struct):
    # TODO: Confirm required behaviour
    def dict(self):
        return structs.asdict(self)

    def dict_without_unset(self):
        return {k: v for k, v in structs.asdict(self).items() if v is not None}

    def dict_ordered(self):
        return {k: getattr(self, k) for k in self.__struct_fields__}


class AppReadDTO(AppDTO):
    id: IntPositive
    created_at: datetime
    updated_at: datetime
    is_active: bool


class AppCreateDTO(AppDTO):
    is_active: bool = True


class AppUpdateDTO(AppDTO):
    is_active: bool = True


class AppUpdateWithIdDTO(AppDTO):
    id: IntPositive
    is_active: bool = True

    @classmethod
    def update_as_columns_clause(cls) -> str:
        return ", ".join([f for f in cls.__struct_fields__])


class AppReadAllPaginationDetailsDTO(AppDTO):
    x_total_count: str
    x_offset: str
    x_limit: str


class AppDeleteAllDTO(AppDTO):
    confirmation_code: str


class AppDeleteResponseDTO(AppDTO):
    id: IntPositive


class AppDeleteAllResponseDTO(AppDTO):
    count: IntNonNegative


class AppBulkActionResultDTO(AppDTO):
    ids: list[IntPositive]
