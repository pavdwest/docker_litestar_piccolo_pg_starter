from asyncpg import UniqueViolationError
from inflection import pluralize
from litestar import Response, post, get, patch, put, delete
from litestar import status_codes
from litestar.exceptions import HTTPException
from msgspec import Struct
from litestar.openapi import ResponseSpec
from enum import StrEnum
import operator

from src.models.base import AppModel
from src.controllers.base import AppController
from src.dtos import (
    AppCreateDTO,
    AppReadDTO,
    AppUpdateDTO,
    AppUpdateWithIdDTO,
    AppSearchDTO,
    AppBulkActionResultDTO,
    AppReadAllPaginationDetailsDTO,
    IntID,
    IntPositive,
    IntNonNegative,
    IntMaxLimit,
)
from src.response_specs import ConflictResponse


class JoinOperator(StrEnum):
    AND: str = "and"
    OR: str = "or"

    def operator_mapping(self):
        if self == JoinOperator.AND:
            return operator.and_
        elif self == JoinOperator.OR:
            return operator.or_


class CrudController(AppController): ...


def generate_crud_controller(
    Model: type[AppModel],
    CreateDTO: type[AppCreateDTO],
    ReadDTO: type[AppReadDTO],
    UpdateDTO: type[AppUpdateDTO],
    UpdateWithIdDTO: type[AppUpdateWithIdDTO],
    SearchDTO: type[AppSearchDTO],
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
    controller_class.UpdateWithIdDTO = UpdateDTO
    controller_class.path = f"{api_version_prefix}/{Model._meta.tablename}"
    controller_class.tags = [Model.humanise()]
    many_endpoints_path = "/many"

    # ResponseSpecs
    ConflictResponseClass = type(f"{Model}ConflictResponse", (Struct,), {})
    ConflictResponseClass.status_code = status_codes.HTTP_409_CONFLICT
    ConflictResponseClass.detail = f"Duplicate key error on key ({Model._meta.primary_key})."


    # Routes
    @post(
        "/",
        description=f"Create a {Model.humanise()}.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_201_CREATED,
        responses={
            status_codes.HTTP_409_CONFLICT: ResponseSpec(
                data_container=ConflictResponse,
                description=f"Cannot create a {Model.humanise()} because one with the same primary key already exists.",
            )
        },
    )
    async def create_one(
        self,
        data: CreateDTO,  # type: ignore
    ) -> ReadDTO:  # type: ignore
        return await Model.create_one(data)
    setattr(controller_class, "create_one", create_one)

    @get(
        "/{id:int}",
        description=f"Retrieve a {Model.humanise()} by id.",
        exclude_from_auth=exclude_from_auth,
    )
    async def read_one(
        self,
        id: IntID,
    ) -> ReadDTO:  # type: ignore
        item = await Model.read_one(id)
        return item
    setattr(controller_class, "read_one", read_one)

    @patch(
        "/{id:int}",
        description=f"Update a {Model.humanise()} by id.",
        exclude_from_auth=exclude_from_auth,
    )
    async def update_one(
        self,
        id: IntID,
        data: UpdateDTO,  # type: ignore
    ) -> ReadDTO:  # type: ignore
        return await Model.update_one(id, data)
    setattr(controller_class, "update_one", update_one)

    @patch(
        "/",
        description=f"Update a {Model.humanise()} with id in the payload.",
        exclude_from_auth=exclude_from_auth,
    )
    async def update_one_with_id(
        self,
        data: UpdateWithIdDTO,  # type: ignore
    ) -> ReadDTO:  # type: ignore
        return await Model.update_one_with_id(data)
    setattr(controller_class, "update_one_with_id", update_one_with_id)

    @put(
        "/",
        description=f"Create or update a {Model.humanise()}.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def upsert_one(
        self,
        data: CreateDTO,  # type: ignore
    ) -> ReadDTO:  # type: ignore
        return await Model.upsert_one(data)
    setattr(controller_class, "upsert_one", upsert_one)

    @delete(
        "/{id:int}",
        description=f"Delete a {Model.humanise()} by id.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_one(
        self,
        id: IntID,
    ) -> None:
        await Model.delete_one(id)
    setattr(controller_class, "delete_one", delete_one)

    @get(
        "/count",
        description=f"Retrieve count of all {Model.humanise()}.",
        exclude_from_auth=exclude_from_auth,
    )
    async def read_count(
        self,
    ) -> int:
        return await Model.count()
    setattr(controller_class, "read_count", read_count)

    @get(
        "/",
        description=f"Retrieve all {pluralize(Model.humanise())}. \
            Paginated with offset and limit. See response headers \
                for total count.",
        exclude_from_auth=exclude_from_auth,
    )
    async def read_all(
        self,
        offset: IntNonNegative = 0,
        limit: IntMaxLimit = read_all_limit_default,
    ) -> list[ReadDTO]:  # type: ignore
        items = await Model.read_all(
            offset=offset,
            limit=min(limit, read_all_limit_max)
        )
        # headers=AppReadAllPaginationDetailsDTO(
        #     x_total_count=str(len(items)),
        #     x_offset=str(offset),
        #     x_limit=str(limit),
        # ).dict(),
        return items
    setattr(controller_class, "read_all", read_all)

    @post(
        many_endpoints_path,
        description=f"Create multiple {Model.humanise_plural()}. \
        Will error out if any item already exists.",
        exclude_from_auth=exclude_from_auth,
    )
    async def create_many(
        self,
        data: list[CreateDTO],  # type: ignore
    ) -> AppBulkActionResultDTO:
        return await Model.create_many(data)
    setattr(controller_class, "create_many", create_many)

    @patch(
        many_endpoints_path,
        description=f"Update multiple {Model.humanise_plural()} with ids. \
        Will error out if any item does not exist.",
        exclude_from_auth=exclude_from_auth,
    )
    async def update_many_with_id(
        self,
        data: list[UpdateWithIdDTO],  # type: ignore
    ) -> AppBulkActionResultDTO:
        return await Model.update_many_with_id(data)
    setattr(controller_class, "update_many_with_id", update_many_with_id)

    @put(
        many_endpoints_path,
        description=f"Create or update multiple {Model.humanise_plural()}. \
        Will update any existing items.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def upsert_many(
        self,
        data: list[CreateDTO],  # type: ignore
    ) -> AppBulkActionResultDTO:
        try:
            return await Model.upsert_many(data)
        except UniqueViolationError as e:
            raise HTTPException(
                status_code=status_codes.HTTP_409_CONFLICT,
                detail=str(e),
            )
    setattr(controller_class, "upsert_many", upsert_many)

    @delete(
        "/",
        description=f"Delete all {Model.humanise_plural()}. See response header 'X-DELETED-COUNT' for number of items deleted.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_204_NO_CONTENT,
        response_class=Response,
    )
    async def delete_all(
        self,
    ) -> None:
        res = await Model.delete_all(force=True)
        return Response(
            status_code=status_codes.HTTP_204_NO_CONTENT,
            content=None,
            headers={
                'X-DELETED-COUNT': str(res.count)
            }
        )
    setattr(controller_class, "delete_all", delete_all)


    @post(
        "/search",
        description=f"Search for {pluralize(Model.humanise())}.",
        exclude_from_auth=exclude_from_auth,
        status_code=status_codes.HTTP_200_OK,
    )
    async def search(
        self,
        data: SearchDTO,  # type: ignore
        join_operator: JoinOperator = JoinOperator.AND,
        offset: IntNonNegative = 0,
        limit: IntMaxLimit = read_all_limit_default,
    ) -> list[ReadDTO]: # type: ignore
        return await Model.search(
            data,
            join_operator.operator_mapping(),
            offset,
            read_all_limit_default
        )
    setattr(controller_class, "search", search)

    return controller_class
