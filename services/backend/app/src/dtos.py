from datetime import datetime, timedelta
from typing import Annotated, Optional
from functools import lru_cache

from litestar.params import Parameter
from msgspec import Struct, structs

from src.constants import STRING_SHORT_LENGTH, STRING_LONG_LENGTH


# Some commonly used constraints
IntID = Annotated[int, Parameter(ge=1)]
StringShort = Annotated[str, Parameter(max_length=STRING_SHORT_LENGTH)]
StringLong = Annotated[str, Parameter(max_length=STRING_LONG_LENGTH)]
IntPositive = Annotated[int, Parameter(ge=1)]
IntNonNegative = Annotated[int, Parameter(ge=0)]
IntMaxLimit = Annotated[int, Parameter(ge=1, le=200)]


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
    is_active: Optional[bool] = True


class AppUpdateDTO(AppDTO):
    is_active: Optional[bool] = None


class AppUpdateWithIdDTO(AppDTO):
    id: IntPositive
    is_active: Optional[bool] = None

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
    id: IntPositive


class AppDeleteAllResponseDTO(AppDTO):
    count: IntNonNegative


class AppBulkActionResultDTO(AppDTO):
    ids: list[IntPositive]


class AppSearchDTO(AppDTO, kw_only=True):
    created_at_min: Optional[datetime] = None
    created_at_max: Optional[datetime] = None
    updated_at_min: Optional[datetime] = None
    updated_at_max: Optional[datetime] = None
    is_active: Optional[bool] = None
