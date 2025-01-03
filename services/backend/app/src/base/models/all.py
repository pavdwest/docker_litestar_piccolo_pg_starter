from functools import lru_cache
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.base.models.base import AppModel


_APP_MODELS: dict[str, type['AppModel']] = {}


def cache_app_model(app_model: type['AppModel']) -> None:
    _APP_MODELS.update({app_model.__name__: app_model})


@lru_cache(maxsize=1)
def get_all_app_models() -> dict[str, type['AppModel']]:
    return _APP_MODELS


@lru_cache()
def get_app_model_by_name(name: str) -> type['AppModel']:
    return _APP_MODELS[name]


def get_all_app_models_list() -> list[type['AppModel']]:
    return list(_APP_MODELS.values())
