from collections.abc import Sequence

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

from src.versions import AppVersion
from src.controllers.all import CONTROLLERS


def create_app(lifespan: Sequence) -> Litestar:
    app = Litestar(
        lifespan=lifespan,
        openapi_config=OpenAPIConfig(
            title="Project API",
            description="Powered by LiteStar: <a href='/schema/openapi.json'>schema.json</a>",
            version=f"{AppVersion.BETA}",
            render_plugins=[
                RapidocRenderPlugin(path="rapidoc"),
                ScalarRenderPlugin(path="scalar"),
                StoplightRenderPlugin(path="stoplight"),
                RedocRenderPlugin(path="redoc"),
                SwaggerRenderPlugin(path="swagger"),
            ],
        ),
        plugins=[GranianPlugin()],
        on_app_init=[],
        middleware=[],
        route_handlers=CONTROLLERS.get_all(),
        debug=True,
    )
    return app
