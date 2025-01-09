from piccolo.columns import Varchar, Integer

# from piccolo.constraint import UniqueConstraint
from src.models.base import generate_model
from src.modules.note.dtos import NoteCreate, NoteRead, NoteUpdate, NoteUpdateWithId


NoteBase = generate_model(
    NoteCreate,
    NoteRead,
    NoteUpdate,
    NoteUpdateWithId
)

class Note(NoteBase):
    # Fields
    title = Varchar(required=True, unique=True)
    body = Varchar(required=True)
    rating = Integer(required=True)
