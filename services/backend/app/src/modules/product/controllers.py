from src.controllers.crud import generate_crud_controller
from .models import Product
from .dtos import ProductCreate, ProductRead, ProductUpdate, ProductUpdateWithId, ProductSearchDTO
from src.versions import ApiVersion


ProductController = generate_crud_controller(
    Model=Product,
    CreateDTO=ProductCreate,
    ReadDTO=ProductRead,
    UpdateDTO=ProductUpdate,
    UpdateWithIdDTO=ProductUpdateWithId,
    SearchDTO=ProductSearchDTO,
    api_version_prefix=ApiVersion.V1,
    exclude_from_auth=True,
)
