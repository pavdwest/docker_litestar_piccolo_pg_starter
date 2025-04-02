from enum import StrEnum
import functools
import math
import time
import types
from typing import Generic, Self, TypeVar
import datetime
import operator
import collections

from piccolo.columns import Timestamptz, BigSerial, Boolean, Column
from piccolo.query import Query
from piccolo.query.methods.insert import Insert
from piccolo.query.functions import Max
from piccolo.table import Table
from piccolo.columns import Varchar, Text  # For checking string types
from inflection import humanize, pluralize

from src.logging.service import logger
from src.dtos import (
    AppCreateDTO,
    AppReadDTO,
    AppUpdateDTO,
    AppUpdateWithIdDTO,
    AppSearchDTO,
    AppBulkActionResultDTO,
    AppDeleteAllResponseDTO,
)
from asyncpg.exceptions import UniqueViolationError
from src.models.exceptions import NotFoundException, ConflictException


class OnConflictAction(StrEnum):
    """Utility class for preventing typos in on conflict actions."""
    DO_NOTHING = "DO NOTHING"
    DO_UPDATE = "DO UPDATE"


# Generic type variables for the types used to create, read, and update
CreateDTOClassType = TypeVar("CreateDTOClassType", bound=AppCreateDTO)
ReadDTOClassType = TypeVar("ReadDTOClassType", bound=AppReadDTO)
UpdateDTOClassType = TypeVar("UpdateDTOClassType", bound=AppUpdateDTO)
UpdateWithIdDTOClassType = TypeVar("UpdateWithIdDTOClassType", bound=AppUpdateWithIdDTO)


class AppModelBase(Table):
    # DTOs
    CreateDTOClass: type[AppCreateDTO] = None
    ReadDTOClass: type[AppReadDTO] = None
    UpdateDTOClass: type[AppUpdateDTO] = None
    UpdateWithIdDTOClass: type[AppUpdateWithIdDTO] = None


# Insert Query Constants
PSQL_QUERY_ALLOWED_MAX_ARGS = 32767


# Function to return datetime in UTC
def datetime_now_utc() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


class AppModel(
    Generic[
        CreateDTOClassType,
        ReadDTOClassType,
        UpdateDTOClassType,
        UpdateWithIdDTOClassType,
    ],
    AppModelBase,
):
    # Model Fields
    id = BigSerial(required=True, primary_key=True)
    created_at = Timestamptz(
        required=True,
        default=datetime_now_utc,
    )
    updated_at = Timestamptz(
        required=True,
        default=datetime_now_utc,
        auto_update=datetime_now_utc,
    )
    is_active = Boolean(required=True, default=True)

    '''
    All multi update and create actions are batched.
    By default, the batch size is determined dynamically
    based on the number of columns and the max number of arguments
    allowed in a PSQL query. This can be overridden with the
    insert_batch_size_override attribute. It can only reduce the batch size.
    The used size is always capped at the dynamic maximum, otherwise inserts would fail.
    This is a Piccolo/Python limitation.
    '''
    insert_batch_size_override = None

    @classmethod
    @functools.lru_cache(maxsize=1)
    def humanise(cls) -> str:
        """Human-readable class name."""
        return humanize(cls.__name__)

    @classmethod
    @functools.lru_cache(maxsize=1)
    def humanise_plural(cls) -> str:
        """Human-readable class name."""
        return pluralize(cls.humanise())

    @classmethod
    async def max_id(cls) -> int:
        return (await cls.select(Max(cls.id)).first().run())["max"] or 0

    @classmethod
    async def create_one(cls, dto: CreateDTOClassType) -> ReadDTOClassType:
        try:
            item = cls(**dto.dict())
            await item.save().run()
            await item.refresh()
            return cls.ReadDTOClass(**item.to_dict())
        except UniqueViolationError as e:
            raise ConflictException(str(e))

    @classmethod
    async def read_one(cls, id: int) -> ReadDTOClassType:
        item = await cls.select().where(cls.id == id).first().run()
        if item is None:
            raise NotFoundException.from_id(id, cls)
        return cls.ReadDTOClass(**item)

    @classmethod
    def attach_offset_and_limit(
        cls,
        q: Query,
        offset: int | None = None,
        limit: int | None = None
    ) -> Query:
        if offset is not None:
            q = q.offset(offset)
        if limit is not None:
            q = q.limit(limit)
        else:
            logger.warning(f"Limit not specified for Read All Query: {q}")
        return q

    @classmethod
    async def read_all(
        cls,
        offset: int | None = None,
        limit: int | None = None
    ) -> list[ReadDTOClassType]:
        q = cls.attach_offset_and_limit(cls.select(), offset, limit)
        items = await q.run()
        return [cls.ReadDTOClass(**item) for item in items]

    @classmethod
    async def update_one(cls, id: int, dto: UpdateDTOClassType) -> ReadDTOClassType:
        item = await cls.objects().where(cls.id == id).first().run()
        if item is None:
            raise NotFoundException.from_id(id, cls)
        await item.update_self(dto.dict_without_unset()).run()
        return cls.ReadDTOClass(**item.to_dict())

    @classmethod
    async def update_one_with_id(cls, dto: UpdateWithIdDTOClassType) -> ReadDTOClassType:
        return await cls.update_one(dto.id, dto)

    @classmethod
    @functools.lru_cache(maxsize=1)
    def _excluded_columns(cls):
        return [
            cls.id,
            cls.created_at,
            cls.updated_at,
            cls.is_active,
        ]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def _excluded_column_names(cls):
        return [c._meta.name for c in cls._excluded_columns()]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def _primary_key_column_names(cls):
        cols = [
            c._meta.name
            for c in cls._meta.columns
            if c._meta.name not in cls._excluded_column_names() and c._meta.unique
        ]
        return cols

    # TODO: Re-evaluate later when composite unique constraint functionality is available
    @classmethod
    @functools.lru_cache(maxsize=1)
    def _add_on_conflict_params(cls, query: Insert) -> Insert:
        """
        Adds conflict resolution parameters to an Insert query.

        Modifies the given Insert query to handle conflicts based on the unique columns
        or constraints defined in the model. This is unique to Postgres' ON CONFLICT clause.
        It sets the conflict target and specifies the action to take (update) along with
        the columns to update in case of a conflict.

        Args:
            query (Insert): The Insert query to modify.

        Returns:
            Insert: The modified Insert query with conflict resolution parameters added.
        """
        unique_cols = cls._unique_columns()
        # If there is only one unique column, use it as the target and update all other columns
        if len(unique_cols) == 1:
            return query.on_conflict(
                target=unique_cols[0],
                action=OnConflictAction.DO_UPDATE,
                values=cls._on_conflict_update_columns(),
            )
        # If there is one unique constraint, use that as the target and update all other columns
        elif len(cls._meta.constraints) == 1:
            chosen_constraint = cls._meta.constraints[0]
            chosen_constraint_cols = cls._on_conflict_update_columns()
            return query.on_conflict(
                target=chosen_constraint._meta.name,
                action=OnConflictAction.DO_UPDATE,
                values=chosen_constraint_cols,
            )
        else:
            logger.warning("NOT SURE WHAT TO DO HERE! On Conflict Statement will likely not work as expected.")
            return query.on_conflict(
                action=OnConflictAction.DO_NOTHING,
            )

    @classmethod
    @functools.lru_cache
    def _get_column_by_name(cls, name: str):
        for c in cls._meta.columns:
            if c._meta.name == name:
                return c
        return None

    @classmethod
    @functools.lru_cache(maxsize=1)
    def _on_conflict_update_columns(cls) -> list[Column]:
        """
        Returns a list of columns that should be updated on conflict. It excludes unique columns
        and columns specified in the excluded_names tuple like id, created_at, updated_at and is_active.

        Args:
            excluded_names (tuple[str]): A tuple of column names to be excluded from the update.

        Returns:
            list: A list of columns to be updated on conflict.
        """
        return [
            c
            for c in cls._meta.columns
            if not c._meta.unique and c._meta.name not in cls._excluded_column_names()
        ]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def _unique_columns(cls) -> list[Column]:
        """
        Retrieve a list of unique columns for the model.
        This method uses an LRU cache to store the result, ensuring that it is only
        computed once and reused for subsequent calls. The cache has a maximum size of 1.
        Returns:
            list: A list of columns that are unique and not excluded by the model.
        """
        return [
            c
            for c in cls._meta.columns
            if c._meta.unique and c._meta.name not in cls._excluded_column_names()
        ]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def _all_column_names(cls):
        return [c._meta.name for c in cls._meta.columns]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def max_batch_size(cls) -> int:
        return int(
            math.floor(PSQL_QUERY_ALLOWED_MAX_ARGS / len(cls._all_column_names()))
        )

    @classmethod
    @functools.lru_cache(maxsize=1)
    def _batch_size(cls) -> int:
        factor = 0.75
        if cls.insert_batch_size_override is not None and cls.insert_batch_size_override > 0:
            return min(cls.insert_batch_size_override, cls.max_batch_size())
        else:
            return int(math.floor(cls.max_batch_size() * factor))

    # A batch generator
    @classmethod
    def batch_generator(cls, items: list[any]):
        batch_number = 0
        batch_size = max(1, cls._batch_size())
        for i in range(0, len(items), batch_size):
            batch_number += 1
            idx_end = min(i + batch_size, len(items))
            logger.info(f"Batch {batch_number} size {idx_end - i}. From item {i+1} to item {idx_end}")
            yield items[i:idx_end]

    @classmethod
    async def insert_batched(
        cls,
        items: list[Self],
    ) -> None:
        for batch in cls.batch_generator(items):
            await cls.insert(*batch).run()

    # TODO: Fix when composite unique constraint functionality is available
    @classmethod
    async def upsert_one(
        cls,
        dto: CreateDTOClassType,
    ) -> ReadDTOClassType:
        item = cls(**dto.dict())
        await cls._add_on_conflict_params(cls.insert(item)).run()
        await item.refresh()
        return cls.ReadDTOClass(**item.to_dict())

    @classmethod
    def group_dicts_by_keys(
        cls,
        dtos: list[AppUpdateDTO],
    ) -> list[list[dict]]:
        """
        Groups dictionaries in a list based on the unique set of keys they possess.

        Args:
            list_of_dicts: A list containing dictionary objects.

        Returns:
            A list of lists, where each inner list contains dictionaries
            that share the exact same set of keys.
        """
        # Use defaultdict to automatically create a new list for a new key set
        grouped_by_keys = collections.defaultdict(list)

        for dto in dtos:
            item_dict = dto.dict_without_unset()

            # Get the keys of the current dictionary
            keys = item_dict.keys()
            # Create a hashable representation of the keys (a sorted tuple)
            # Sorting ensures that the order of keys doesn't matter
            key_tuple = tuple(sorted(keys))
            # Append the dictionary to the list associated with this key set
            grouped_by_keys[key_tuple].append(item_dict)

        # Return the lists of dictionaries (the values of our defaultdict)
        return list(grouped_by_keys.values())

    @classmethod
    async def update_many_with_id(
        cls,
        dtos: list[UpdateWithIdDTOClassType],
    ) -> AppBulkActionResultDTO:
        grouped_items = cls.group_dicts_by_keys(dtos)
        ids = []
        for i, group in enumerate(grouped_items):
            logger.info(f"Group {i+1} size {len(group)}")
            batched_group = cls.batch_generator(group)
            for batch in batched_group:
                items = [cls(**item) for item in batch]
                cols_to_update = [getattr(cls, c) for c in batch[0].keys() if c != "id" and batch[0][c] is not None]
                q = cls.insert(
                    *items
                ).on_conflict(
                    action=OnConflictAction.DO_UPDATE,
                    values=cols_to_update + [cls.updated_at],
                    target=(cls.id)
                )
                res = await q.run()
                ids.extend([item["id"] for item in res])
        return AppBulkActionResultDTO(ids=ids)

    @classmethod
    async def create_many(
        cls, dtos: list[CreateDTOClassType]
    ) -> AppBulkActionResultDTO:
        batch_res = []
        start = time.monotonic()
        try:
            for batch in cls.batch_generator(dtos):
                q = cls.insert(*[cls(**i.dict()) for i in batch]).run()
                batch_res.append(await q)
            logger.info(f"Time taken: {time.monotonic() - start} seconds.")

            return AppBulkActionResultDTO(
                ids=[r["id"] for r in [r for batch in batch_res for r in batch]]
            )
        except UniqueViolationError as e:
            raise ConflictException(str(e))

    @classmethod
    async def upsert_many(
        cls, dtos: list[CreateDTOClassType]
    ) -> AppBulkActionResultDTO:
        batch_res = []
        # TODO: Concat all exceptions into batch
        try:
            start = time.monotonic()
            for batch in cls.batch_generator(dtos):
                q = cls._add_on_conflict_params(
                    cls.insert(*[cls(**i.dict()) for i in batch])
                ).run()
                batch_res.append(await q)
            logger.info(f"Time taken: {time.monotonic() - start} seconds.")

            return AppBulkActionResultDTO(
                ids=[r["id"] for r in [r for batch in batch_res for r in batch]]
            )
        except UniqueViolationError as e:
            raise ConflictException(str(e))

    @classmethod
    async def delete_one(cls, id: int) -> None:
        await cls.delete().where(cls.id == id).run()

    @classmethod
    async def delete_all(cls, force: bool = False) -> AppDeleteAllResponseDTO:
        count = await cls.count().run()
        res = await cls.delete(force).run()
        logger.info(f"Deleted {count} items.")
        return AppDeleteAllResponseDTO(count=count)

    @classmethod
    async def search(
        cls,
        dto: AppSearchDTO,
        join_operator: operator,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[ReadDTOClassType]:
        dto_dict = dto.dict_without_unset()
        clauses = []
        for key, value in dto_dict.items():
            if key.endswith("_min"):
                key = key.removesuffix("_min")
                clauses.append((getattr(cls, key) >= value))
            elif key.endswith("_max"):
                key = key.removesuffix("_max")
                clauses.append((getattr(cls, key) <= value))
            elif issubclass(getattr(cls, key).__class__, (Varchar, Text)):
                clauses.append((getattr(cls, key).ilike(f"%{value}%")))
            else:
                clauses.append((getattr(cls, key) == value))
        q = cls.select().where(functools.reduce(join_operator, clauses))
        return await cls.attach_offset_and_limit(q, offset, limit).run()


def generate_model(
    ClassName: str,
    CreateDTO: type[CreateDTOClassType],
    ReadDTO: type[ReadDTOClassType],
    UpdateDTO: type[UpdateDTOClassType],
    UpdateWithIdDTO: type[UpdateWithIdDTOClassType],
) -> type[AppModel]:
    ModelClass = types.new_class(
        ClassName,
        (AppModel[
            CreateDTO,
            ReadDTO,
            UpdateDTO,
            UpdateWithIdDTO,
        ],),
        {},
        lambda ns: ns.update({
            'CreateDTOClass': CreateDTO,
            'ReadDTOClass': ReadDTO,
            'UpdateDTOClass': UpdateDTO,
            'UpdateWithIdDTOClass': UpdateWithIdDTO,
        })
    )
    return ModelClass
