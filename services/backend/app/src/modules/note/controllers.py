from src.base.controllers.base import generate_crud_controller
from src.modules.note.models import Note
from src.modules.note.dtos import NoteCreate, NoteRead, NoteUpdate
from src.base.versions import ApiVersion


NoteController = generate_crud_controller(
    Model=Note,
    CreateDTO=NoteCreate,
    ReadDTO=NoteRead,
    UpdateDTO=NoteUpdate,
    api_version_prefix=ApiVersion.V1,
    exclude_from_auth=True,
)
