from datetime import datetime
from typing import Annotated
from functools import lru_cache

from litestar.params import Parameter
from msgspec import Struct, structs

from src.models.constants import STRING_SHORT_LENGTH, STRING_LONG_LENGTH


# Some commonly used constraints
IntID = Annotated[int, Parameter(ge=1, le=2**63 - 1)]
StringShort = Annotated[str, Parameter(min_length=1, max_length=STRING_SHORT_LENGTH)]
StringLong = Annotated[str, Parameter(min_length=1, max_length=STRING_LONG_LENGTH)]
IntPositive = Annotated[int, Parameter(ge=1)]
IntNonNegative = Annotated[int, Parameter(ge=0)]
IntMaxLimit = Annotated[int, Parameter(ge=1, le=200)]
DatetimeMin = Annotated[datetime, Parameter(ge=datetime(1970, 1, 1))]


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
    id: IntID
    created_at: DatetimeMin
    updated_at: DatetimeMin
    is_active: bool


class AppCreateDTO(AppDTO):
    is_active: bool = True


class AppUpdateDTO(AppDTO):
    is_active: bool = True


class AppUpdateWithIdDTO(AppDTO):
    id: IntID
    is_active: bool = True

    @classmethod
    @lru_cache(maxsize=1)
    def update_as_columns_clause(cls) -> str:
        return ", ".join([f for f in cls.__struct_fields__])


class AppReadAllPaginationDetailsDTO(AppDTO):
    x_total_count: str
    x_offset: str
    x_limit: str


class AppDeleteAllDTO(AppDTO):
    confirmation_code: str


class AppDeleteResponseDTO(AppDTO):
    id: IntID


class AppDeleteAllResponseDTO(AppDTO):
    count: IntNonNegative


class AppBulkActionResultDTO(AppDTO):
    ids: list[IntID]
