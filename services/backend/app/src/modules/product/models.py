from piccolo.columns import Varchar, Integer

# from piccolo.constraint import UniqueConstraint
from src.models.base import generate_model
from src.modules.product.dtos import ProductCreate, ProductRead, ProductUpdate, ProductUpdateWithId


ProductBase = generate_model(
    'ProductBase',
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductUpdateWithId,
)

class Product(ProductBase):
    title = Varchar(required=True, unique=True)
    description = Varchar(required=True)
    price = Integer(required=True)
