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


IntRating = Annotated[int, Meta(ge=1, le=5)]


class NoteCreate(AppCreateDTO, kw_only=True):
    title: StringShort
    body: StringLong
    rating: IntRating


class NoteRead(AppReadDTO):
    title: StringShort
    body: StringLong
    rating: IntRating


class NoteUpdate(AppUpdateDTO):
    title: Optional[StringShort] = None
    body: Optional[StringLong] = None
    rating: Optional[IntRating] = None


class NoteUpdateWithId(AppUpdateWithIdDTO):
    title: Optional[StringShort] = None
    body: Optional[StringLong] = None
    rating: Optional[IntRating] = None
