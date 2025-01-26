from litestar import status_codes
from msgspec import Struct

# e.g.
# @get(
#     path="/items/{pk:int}",
#     responses={
#         404: ResponseSpec(
#             data_container=ItemNotFound, description="Item was removed or not found"
#         )
#     },
# )


class ConflictResponse(Struct):
    status_code: int = status_codes.HTTP_409_CONFLICT
    detail: str = "Duplicate key error on key (id)."
