from typing import Sequence

from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import (
    StoplightRenderPlugin,
    ScalarRenderPlugin,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    SwaggerRenderPlugin,
)
from litestar_granian import GranianPlugin

from src.config import PROJECT_NAME
from src.versions import AppVersion
from src.controllers.all import CONTROLLERS
from src.lifespan import _ON_INIT, _MIDDLEWARE


def create_app(lifespan: Sequence) -> Litestar:
    app = Litestar(
        lifespan=lifespan,
        openapi_config=OpenAPIConfig(
            title=f"{PROJECT_NAME} API v{AppVersion.BETA}",
            description="Powered by LiteStar",
            version=f"{AppVersion.BETA}",
            render_plugins=[
                StoplightRenderPlugin(path="stoplight"),
                ScalarRenderPlugin(path="scalar"),
                RapidocRenderPlugin(path="rapidoc"),
                RedocRenderPlugin(path="redoc"),
                SwaggerRenderPlugin(path="swagger"),
            ],
        ),
        plugins=[GranianPlugin()],
        on_app_init=_ON_INIT,
        middleware=_MIDDLEWARE,
        route_handlers=CONTROLLERS.get_all(),
        debug=True,
    )
    return app
