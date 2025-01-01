from typing import Optional, Annotated

from pydantic import Field

from src.base.dtos import AppCreateDTO, AppReadDTO, AppUpdateDTO


class NoteCommon:
    title: str
    body: str
    rating: Annotated[int, Field(ge=1, le=5)]



class NoteCreate(AppCreateDTO, NoteCommon):
    ...


class NoteRead(AppReadDTO, NoteCommon):
    ...


class NoteUpdate(AppUpdateDTO):
    title: Optional[str] = None
    body: Optional[str] = None
    rating: Annotated[Optional[int], Field(ge=1, le=5)] = None
