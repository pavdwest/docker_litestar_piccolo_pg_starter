from typing import Annotated

from asyncpg import UniqueViolationError
from inflection import pluralize
from litestar import Controller, post, get, patch, put, delete
from litestar.exceptions import HTTPException
from litestar import status_codes
from pydantic import conint, NonNegativeInt, Field, PositiveInt

from src.base.models.base import AppModel
from src.base.dtos import (
    AppCreateDTO,
    AppReadDTO,
    AppUpdateDTO,
    AppBulkActionResultDTO,
    AppDeleteAllDTO,
    AppDeleteAllResponseDTO,
)
from src.base.exceptions import NotFoundException


class AppController(Controller):
    ...


class CrudController(AppController):
    ...


def generate_crud_controller(
    Model: type[AppModel],
    CreateDTO: type[AppCreateDTO],
    ReadDTO: type[AppReadDTO],
    UpdateDTO: type[AppUpdateDTO],
    api_version_prefix: str,
    exclude_from_auth: bool = False,
    read_all_limit_default: int = 100,
    read_all_limit_max: int = 200,
) -> type[CrudController]:

    controller_class = type(f"{Model}Controller", (CrudController,), {})
    controller_class.Model = Model
    controller_class.CreateDTO = CreateDTO
    controller_class.ReadDTO = ReadDTO
    controller_class.UpdateDTO = UpdateDTO
    controller_class.path = f"{api_version_prefix}/{Model._meta.tablename}"
    controller_class.tags = [Model.humanise()]

    many_endpoints_path = "/many"

    @post(
        '/',
        description=f"Create a {Model.humanise()}.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_one(
        self,
        data: CreateDTO,   # type: ignore
    ) -> ReadDTO:          # type: ignore
        try:
            return await Model.create_one(data)
        except UniqueViolationError as e:
            raise HTTPException(
                status_code=status_codes.HTTP_409_CONFLICT,
                detail=str(e),
            )
    setattr(controller_class, 'create_one', create_one)


    @get(
        '/{id:int}',
        description=f"Retrieve a {Model.humanise()} by id.",
        exclude_from_auth=exclude_from_auth,
    )
    async def read_one(
        self,
        id: Annotated[int, Field(gt=0)],
    ) -> ReadDTO:          # type: ignore
        try:
            item = await Model.read_one(id)
            return item
        except NotFoundException as e:
            raise e.http_exception()
    setattr(controller_class, 'read_one', read_one)


    @patch(
        '/{id:int}',
        description=f"Update a {Model.humanise()} by id.",
        exclude_from_auth=exclude_from_auth,
    )
    async def update_one(
        self,
        id: Annotated[int, Field(gt=0)],
        data: UpdateDTO,   # type: ignore
    ) -> ReadDTO:          # type: ignore
        try:
            return await Model.update_one(id, data)
        except NotFoundException as e:
            raise e.http_exception()
    setattr(controller_class, 'update_one', update_one)


    @put(
        '/',
        description=f"Create or update a {Model.humanise()}.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def upsert_one(
        self,
        data: CreateDTO,        # type: ignore
    ) -> ReadDTO:               # type: ignore
        return await Model.upsert_one(data)
    setattr(controller_class, 'upsert_one', upsert_one)


    @delete(
        '/{id:int}',
        description=f"Delete a {Model.humanise()} by id.",
        exclude_from_auth=exclude_from_auth,
    )
    async def delete_one(
        self,
        id: Annotated[int, Field(gt=0)],
    ) -> None:
        try:
            await Model.delete_one(id)
        except NotFoundException as e:
            raise e.http_exception()
    setattr(controller_class, 'delete_one', delete_one)


    @get(
        '/',
        description=f"Retrieve all {pluralize(Model.humanise())}.",
        exclude_from_auth=exclude_from_auth,
    )
    async def read_all(
        self,
        offset: NonNegativeInt = 0,
        limit: Annotated[int, Field(gt=0)] = read_all_limit_default,
    ) -> list[ReadDTO]:                     # type: ignore
        return await Model.read_all(offset=offset, limit=min(limit, read_all_limit_max))
    setattr(controller_class, 'read_all', read_all)


    @post(
        many_endpoints_path,
        description=f"Create multiple {Model.humanise_plural()}. \
        Will error out if any item already exists.",
        exclude_from_auth=exclude_from_auth,
    )
    async def create_many(
        self,
        data: list[CreateDTO],      # type: ignore
    ) -> AppBulkActionResultDTO:
        try:
            return await Model.create_many(data)
        except UniqueViolationError as e:
            raise HTTPException(
                status_code=status_codes.HTTP_409_CONFLICT,
                detail=str(e),
            )
    setattr(controller_class, 'create_many', create_many)


    @put(
        many_endpoints_path,
        description=f"Create or update multiple {Model.humanise_plural()}. \
        Will update any existing items.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def upsert_many(
        self,
        data: list[CreateDTO],      # type: ignore
    ) -> AppBulkActionResultDTO:
        try:
            return await Model.upsert_many(data)
        except UniqueViolationError as e:
            raise HTTPException(
                status_code=status_codes.HTTP_409_CONFLICT,
                detail=str(e),
            )
    setattr(controller_class, 'upsert_many', upsert_many)


    # @delete(
    #     '/',
    #     description=f"Delete all {Model.humanise_plural()}.\
    #     The following case-sensitive Confirmation Code must be provided as \
    #     payload otherwise this request will not be authorised: \
    #     'DELETE ALL {Model.humanise_plural()}'.",
    #     status_code=status_codes.HTTP_200_OK,
    #     exclude_from_auth=exclude_from_auth,
    # )
    # async def delete_all(
    #     self,
    #     data: AppDeleteAllDTO,
    # ) -> None:
    #     await Model.delete_all(force=True)
    # setattr(controller_class, 'delete_all', delete_all)

    # TODO: Fix this
    @delete(
        '/',
        description=f"Delete all {Model.humanise_plural()}.",
        exclude_from_auth=exclude_from_auth,
    )
    async def delete_all(
        self,
    ) -> None:
        await Model.delete_all(force=True)
    setattr(controller_class, 'delete_all', delete_all)


    return controller_class
