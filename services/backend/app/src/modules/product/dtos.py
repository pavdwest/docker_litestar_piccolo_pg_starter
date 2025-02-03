from typing import Optional, Annotated
from msgspec import Meta

from src.dtos import (
    AppCreateDTO,
    AppReadDTO,
    AppUpdateDTO,
    AppUpdateWithIdDTO,
    StringShort,
    StringLong,
)


Price = Annotated[float, Meta(ge=0.01)]


class ProductCreate(AppCreateDTO, kw_only=True):
    title: StringShort
    description: StringLong
    price: Price


class ProductRead(AppReadDTO):
    title: StringShort
    description: StringLong
    price: Price


class ProductUpdate(AppUpdateDTO):
    title: Optional[StringShort] = None
    description: Optional[StringLong] = None
    price: Optional[Price] = None


class ProductUpdateWithId(AppUpdateWithIdDTO):
    title: Optional[StringShort] = None
    description: Optional[StringLong] = None
    price: Optional[Price] = None
