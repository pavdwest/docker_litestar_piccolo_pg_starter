from piccolo.columns import Varchar, Integer

# from piccolo.constraint import UniqueConstraint
from src.models.base import AppModel
from src.modules.note.dtos import NoteCreate, NoteRead, NoteUpdate, NoteUpdateWithId


class Note(
    AppModel[
        NoteCreate,
        NoteRead,
        NoteUpdate,
        NoteUpdateWithId
    ],
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
