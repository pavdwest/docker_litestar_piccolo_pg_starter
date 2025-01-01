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

from src.base.versions import ApiVersion
from src.monkey_patches.all import apply_all_monkey_patches
from src.base.controllers.all import get_all_controllers


def create_app(lifespan: Sequence) -> Litestar:
    apply_all_monkey_patches()

    app = Litestar(
        lifespan=lifespan,
        openapi_config=OpenAPIConfig(
            title=f"Pureformant API",
            description='Powered by LiteStar',
            version=f"{ApiVersion.V1}",
            render_plugins=[
                StoplightRenderPlugin(path='stoplight'),
                ScalarRenderPlugin(path='scalar'),
                RapidocRenderPlugin(path='rapidoc'),
                RedocRenderPlugin(path='redoc'),
                SwaggerRenderPlugin(path='swagger'),
            ],
        ),
        route_handlers=get_all_controllers(),
        debug=True,
    )
    return app
