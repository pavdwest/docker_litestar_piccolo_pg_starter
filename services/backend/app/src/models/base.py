from enum import StrEnum
import math
import time
from typing import Generic, Self, TypeVar
from datetime import datetime
from functools import lru_cache

from piccolo.table import Table
from piccolo.columns import Timestamp, BigSerial, Boolean
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.query.methods.insert import Insert
from piccolo.query.functions import Max
from inflection import humanize, pluralize

from src.logging.service import logger
from src.models.all import cache_app_model
from src.dtos import (
    AppCreateDTO,
    AppReadDTO,
    AppUpdateDTO,
    AppUpdateWithIdDTO,
    AppBulkActionResultDTO,
    AppDeleteAllResponseDTO,
)
from asyncpg.exceptions import UniqueViolationError
from src.models.exceptions import NotFoundException, UniquenessException


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


PSQL_QUERY_ALLOWED_MAX_ARGS = 32767
INSERT_BATCHED_DEFAULT_SIZE = 5000


class AppModel(
    Generic[
        CreateDTOClassType,
        ReadDTOClassType,
        UpdateDTOClassType,
        UpdateWithIdDTOClassType,
    ],
    AppModelBase,
):
    id = BigSerial(required=True, primary_key=True)
    created_at = Timestamp(required=True, default=TimestampNow)
    updated_at = Timestamp(
        required=True, default=TimestampNow, auto_update=datetime.now
    )
    is_active = Boolean(required=True, default=True)

    def __init_subclass__(cls, *args, **kwargs):
        cache_app_model(cls)
        return super().__init_subclass__(*args, **kwargs)

    @classmethod
    @lru_cache(maxsize=1)
    def humanise(cls) -> str:
        """Human-readable class name."""
        return humanize(cls.__name__)

    @classmethod
    @lru_cache(maxsize=1)
    def humanise_plural(cls) -> str:
        """Human-readable class name."""
        return pluralize(cls.humanise())

    @classmethod
    async def max_id(cls) -> int:
        return await cls.select(Max(cls.id)).first().run()

    @classmethod
    async def create_one(cls, dto: CreateDTOClassType) -> ReadDTOClassType:
        try:
            item = cls(**dto.dict())
            await item.save().run()
            await item.refresh()
            return cls.ReadDTOClass(**item.to_dict())
        except UniqueViolationError as e:
            raise UniquenessException(str(e))

    @classmethod
    async def read_one(cls, id: int) -> ReadDTOClassType:
        item = await cls.select().where(cls.id == id).first().run()
        if item is None:
            raise NotFoundException.from_id(id)
        return cls.ReadDTOClass(**item)

    @classmethod
    async def read_all(
        cls,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ReadDTOClassType]:
        items = await cls.select().offset(offset).limit(limit).run()
        return [cls.ReadDTOClass(**item) for item in items]

    @classmethod
    async def update_one(cls, id: int, dto: UpdateDTOClassType) -> ReadDTOClassType:
        item = await cls.objects().where(cls.id == id).first().run()
        if item is None:
            raise NotFoundException.from_id(id)
        await item.update_self(dto.dict_without_unset()).run()
        return cls.ReadDTOClass(**item.to_dict())

    @classmethod
    async def update_one_with_id(cls, dto: UpdateWithIdDTOClassType) -> ReadDTOClassType:
        return await cls.update_one(dto.id, dto)

    @classmethod
    @lru_cache(maxsize=1)
    def _excluded_column_names(cls):
        return ["id", "created_at", "updated_at", "is_active"]

    @classmethod
    @lru_cache(maxsize=1)
    def _model_primary_key_column_names(cls):
        cols = [
            c._meta.name
            for c in cls._meta.columns
            if c._meta.name not in cls._excluded_column_names() and c._meta.unique
        ]
        return cols

    # TODO: Re-evaluate later when composite unique constraint functionality is available
    @classmethod
    @lru_cache(maxsize=1)
    def _add_on_conflict_params(cls, query: Insert) -> Insert:
        unique_cols = cls._unique_columns()
        # If there is only one unique column, use it as the target and update all other columns
        if len(unique_cols) == 1:
            return query.on_conflict(
                target=unique_cols[0],
                action=OnConflictAction.DO_UPDATE,
                values=cls._on_conflict_update_columns(
                    tuple([unique_cols[0]._meta.name])
                ),
            )
        # If there is one unique constraint, use that as the target and update all other columns
        else:
            if len(cls._meta.constraints) == 1:
                chosen_constraint = cls._meta.constraints[0]
                chosen_constraint_cols = cls._on_conflict_update_columns(
                    tuple([chosen_constraint._meta.params["_unique_columns"]])
                )
                return query.on_conflict(
                    target=chosen_constraint._meta.name,
                    action=OnConflictAction.DO_UPDATE,
                    values=chosen_constraint_cols,
                )
            else:
                logger.warning("NOT SURE WHAT TO DO HERE!")
        return query

    @classmethod
    @lru_cache
    def _get_column_by_name(cls, name: str):
        for c in cls._meta.columns:
            if c._meta.name == name:
                return c
        return None

    @classmethod
    @lru_cache(maxsize=1)
    def _on_conflict_update_columns(cls, excluded_names: tuple[str]):
        return [
            c
            for c in cls._meta.columns
            if not c._meta.unique and c._meta.name not in cls._excluded_column_names()
        ]

    @classmethod
    @lru_cache(maxsize=1)
    def _unique_columns(cls):
        return [
            c
            for c in cls._meta.columns
            if c._meta.unique and c._meta.name not in cls._excluded_column_names()
        ]

    @classmethod
    @lru_cache(maxsize=1)
    def _all_column_names(cls):
        return [c._meta.name for c in cls._meta.columns]

    @classmethod
    @lru_cache(maxsize=1)
    def max_batch_size(cls) -> int:
        return int(
            math.floor(PSQL_QUERY_ALLOWED_MAX_ARGS / len(cls._all_column_names()))
        )

    @classmethod
    def _idx_end(cls, i: int, batch_size: int, total_items: int) -> int:
        return min(i + batch_size, total_items)

    @classmethod
    @lru_cache(maxsize=1)
    def _batch_size(cls) -> int:
        factor = 0.75
        return int(math.floor(factor * cls.max_batch_size()))

    @classmethod
    async def insert_batched(
        cls,
        items: list[Self],
        batch_size: int = INSERT_BATCHED_DEFAULT_SIZE,
    ) -> None:
        batch_size = min(batch_size, cls._batch_size())
        for i in range(0, len(items), batch_size):
            idx_end = cls._idx_end(i, batch_size, len(items))
            await cls.insert(*items[i:idx_end]).run()

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
    async def create_many(
        cls, dtos: list[CreateDTOClassType]
    ) -> AppBulkActionResultDTO:
        batch_size = cls._batch_size()
        batch_res = []
        batch_number = 1

        start = time.monotonic()
        try:
            for i in range(0, len(dtos), batch_size):
                idx_end = cls._idx_end(i, batch_size, len(dtos))
                batch_items = dtos[i:idx_end]
                q = cls.insert(*[cls(**i.dict()) for i in batch_items]).run()
                batch_res.append(await q)
                logger.info(
                    f"Batch {batch_number} size {len(batch_items)}: items idx={i} to idx={i+len(batch_items)-1} inserted."
                )
                batch_number += 1
            logger.info(f"Time taken: {time.monotonic() - start} seconds.")

            return AppBulkActionResultDTO(
                ids=[r["id"] for r in [r for batch in batch_res for r in batch]]
            )
        except UniqueViolationError as e:
            raise UniquenessException(str(e))

    @classmethod
    async def update_many_with_id(
        cls, dtos: list[UpdateWithIdDTOClassType]
    ) -> AppBulkActionResultDTO:
        if len(dtos) > 0:
            all_columns = cls._all_column_names()
            if "id" not in all_columns:
                raise ValueError("The table must have an 'id' column as the primary key.")
            batch_size = cls._batch_size()
            update_columns = [c for c in cls._all_column_names() if c not in cls._excluded_column_names()]
            updated_ids = []

            for i in range(0, len(dtos), batch_size):
                # Create the VALUES clause
                values = []
                for record in dtos[i:i + batch_size]:
                    record_values = []
                    for column in all_columns:
                        value = getattr(record, column, None)
                        if value is None:
                            record_values.append("NULL")
                        elif isinstance(value, str):
                            record_values.append(f"'{value.replace('\'', '\'\'')}'")  # Escape single quotes
                        else:
                            record_values.append(str(value))
                    values.append(f"({', '.join(record_values)})")
                values_clause = ",\n        ".join(values)

                # Generate SET clause dynamically
                set_clause = ",\n    ".join(
                    [f"{column} = COALESCE(v.{column}, t.{column})" for column in update_columns]
                )

                # Generate the SQL query
                raw_query = f"""
                UPDATE {cls._meta.tablename} AS t
                SET
                    {set_clause},
                    updated_at = NOW()
                FROM (
                    VALUES
                        {values_clause}
                ) AS v({', '.join(all_columns)})
                WHERE t.id = v.id
                RETURNING t.id;
                """
                res = await cls.raw(raw_query).run()
                updated_ids.extend([r["id"] for r in res])
        return AppBulkActionResultDTO(ids=updated_ids)

    @classmethod
    async def upsert_many(
        cls, dtos: list[CreateDTOClassType]
    ) -> AppBulkActionResultDTO:
        batch_size = cls._batch_size()
        batch_res = []
        batch_number = 1

        start = time.monotonic()
        for i in range(0, len(dtos), batch_size):
            idx_end = cls._idx_end(i, batch_size, len(dtos))
            batch_items = dtos[i:idx_end]
            q = cls._add_on_conflict_params(
                cls.insert(*[cls(**i.dict()) for i in batch_items])
            ).run()
            batch_res.append(await q)
            logger.info(
                f"Batch {batch_number} size {len(batch_items)}: items idx={i} to idx={i+len(batch_items)-1} inserted."
            )
            batch_number += 1
        logger.info(f"Time taken: {time.monotonic() - start} seconds.")

        return AppBulkActionResultDTO(
            ids=[r["id"] for r in [r for batch in batch_res for r in batch]]
        )

    @classmethod
    async def delete_one(cls, id: int) -> None:
        await cls.delete().where(cls.id == id).run()

    @classmethod
    async def delete_all(cls, force: bool = False) -> AppDeleteAllResponseDTO:
        count = await cls.count().run()
        res = await cls.delete(force=True).run()
        logger.info(f"Deleted {count} items.")
        return AppDeleteAllResponseDTO(count=count)
