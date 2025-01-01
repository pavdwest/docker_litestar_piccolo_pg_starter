from datetime import datetime
import abc

from pydantic import BaseModel, NonNegativeInt, PositiveInt


# Abstract
class AppDTO(BaseModel, abc.ABC):
    ...


class AppReadDTO(AppDTO, abc.ABC):
    id: int
    created_at: datetime
    updated_at: datetime
    deactivated: bool


class AppCreateDTO(AppDTO, abc.ABC):
    deactivated: bool = False


class AppUpdateDTO(AppDTO, abc.ABC):
    deactivated: bool = False


class AppDeleteAllDTO(AppDTO):
    confirmation_code: str


class AppDeleteResponseDTO(AppDTO):
    id: int


class AppDeleteAllResponseDTO(AppDTO):
    count: NonNegativeInt


class AppBulkActionResultDTO(AppDTO):
    ids: list[PositiveInt]
