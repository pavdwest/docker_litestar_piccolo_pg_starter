from src.controllers.base import AppController
from src.manifest import ClassManifest


CONTROLLERS = ClassManifest[AppController](
    [
        "src.modules.home.controllers.HomeController",
        "src.modules.product.controllers.ProductController",
    ]
)
