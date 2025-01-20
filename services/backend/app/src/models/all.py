from src.models.base import AppModel
from src.manifest import ClassManifest


MODELS = ClassManifest[AppModel](
    [
        "src.modules.note.models.Note",
    ]
)
