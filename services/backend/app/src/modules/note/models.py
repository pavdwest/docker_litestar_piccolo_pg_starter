from piccolo.columns import Varchar, Integer
# from piccolo.constraint import UniqueConstraint
from src.base.models.base import AppModel, SharedModelMixin
from src.modules.note.dtos import NoteCreate, NoteRead, NoteUpdate


class Note(
    AppModel[
        NoteCreate,
        NoteRead,
        NoteUpdate
    ],
    SharedModelMixin,
):
    # Fields
    title = Varchar(required=True, unique=True)
    body = Varchar(required=True)
    rating = Integer(required=True)

    # Constraints - try catch?
    # unique_body_rating = UniqueConstraint(['body', 'rating'])

    # DTO info
    CreateDTOClass = NoteCreate
    ReadDTOClass = NoteRead
    UpdateDTOClass = NoteUpdate
