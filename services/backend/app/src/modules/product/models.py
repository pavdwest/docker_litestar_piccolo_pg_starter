from piccolo.columns import DoublePrecision

from src.models.base import generate_model
from src.models.column_types import StringShortPk, StringLong
from .dtos import ProductCreate, ProductRead, ProductUpdate, ProductUpdateWithId


ProductBase = generate_model(
    'ProductBase',
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductUpdateWithId,
)

class Product(ProductBase):
    title = StringShortPk()
    description = StringLong()
    price = DoublePrecision(required=True)
