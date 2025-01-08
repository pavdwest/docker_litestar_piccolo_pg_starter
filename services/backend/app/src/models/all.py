from functools import lru_cache
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.base import AppModel


_APP_MODELS: dict[str, type["AppModel"]] = {}


def init_all_app_models() -> None:
    """Import all AppModel subclasses here to correctly init them."""
    from src.modules.note.models import Note


def cache_app_model(app_model: type["AppModel"]) -> None:
    _APP_MODELS.update({app_model.__name__: app_model})


@lru_cache(maxsize=1)
def get_all_app_models() -> dict[str, type["AppModel"]]:
    init_all_app_models()
    return _APP_MODELS


@lru_cache()
def get_app_model_by_name(name: str) -> type["AppModel"]:
    return get_all_app_models()[name]


@lru_cache()
def get_all_app_models_list() -> tuple[type["AppModel"]]:
    return tuple(get_all_app_models().values())
