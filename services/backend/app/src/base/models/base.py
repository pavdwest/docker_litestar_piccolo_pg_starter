from enum import StrEnum
import time
from typing import Generic, TypeVar
from datetime import datetime
from functools import lru_cache

from piccolo.table import Table
from piccolo.columns import Timestamp, BigSerial, Boolean
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.query.methods.insert import Insert
from piccolo.query.functions import Max, Count
from inflection import humanize, pluralize

from src.logging.service import logger
from src.base.models.all import cache_app_model
from src.base.dtos import (
    AppCreateDTO,
    AppReadDTO,
    AppUpdateDTO,
    AppBulkActionResultDTO,
    AppDeleteAllResponseDTO,
)
from src.base.models.exceptions import NotFoundException


class OnConflictAction(StrEnum):
    """Utility class for preventing typos in on conflict actions."""
    DO_NOTHING = 'DO NOTHING'
    DO_UPDATE = 'DO UPDATE'


# Generic typevars for create, read, and update DTOs
CreateDTOClassType = TypeVar('CreateDTOClassType', bound=AppCreateDTO)
ReadDTOClassType = TypeVar('ReadDTOClassType', bound=AppReadDTO)
UpdateDTOClassType = TypeVar('UpdateDTOClassType', bound=AppUpdateDTO)


class SharedModelMixin:
        ...


class TenantModelMixin:
    ...


class AppModel(
    Generic[
        CreateDTOClassType,
        ReadDTOClassType,
        UpdateDTOClassType,
    ],
    Table,
):
    id = BigSerial(required=True, primary_key=True)
    created_at = Timestamp(required=True, default=TimestampNow)
    updated_at = Timestamp(required=True, default=TimestampNow, auto_update=datetime.now)
    deactivated = Boolean(required=True, default=False)

    # DTOs
    CreateDTOClass: type[AppCreateDTO] = None
    ReadDTOClass: type[AppReadDTO] = None
    UpdateDTOClass: type[AppUpdateDTO] = None

    def __init_subclass__(
        cls,
        *args,
        **kwargs
    ):
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
        item = cls(**dto.model_dump())
        await item.save().run()
        await item.refresh()
        return cls.ReadDTOClass.model_construct(**item.to_dict())

    @classmethod
    async def read_one(cls, id: int) -> ReadDTOClassType:
        item = await cls.select().where(cls.id == id).first().run()
        if item is None:
            raise NotFoundException.from_id(id)
        return cls.ReadDTOClass.model_construct(**item)

    @classmethod
    async def read_all(
        cls,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ReadDTOClassType]:
        items = await cls.select().offset(offset).limit(limit).run()
        return [cls.ReadDTOClass.model_construct(**item) for item in items]

    @classmethod
    async def update_one(cls, id: int, dto: UpdateDTOClassType) -> ReadDTOClassType:
        item = await cls.objects().where(cls.id == id).first().run()
        if item is None:
            raise NotFoundException.from_id(id)
        await item.update_self(dto.model_dump(exclude_unset=True)).run()
        return cls.ReadDTOClass.model_construct(**item.to_dict())

    @classmethod
    @lru_cache(maxsize=1)
    def model_primary_key_field_names(cls):
        excluded = ['id', 'created_at', 'updated_at', 'deactivated']
        cols = [c._meta.name for c in cls._meta.columns if c._meta.name not in excluded and c._meta.unique]
        return cols

    @classmethod
    @lru_cache(maxsize=1)
    def add_on_conflict_params(cls, query: Insert) -> Insert:
        unique_cols = cls.unique_columns()
        # If there is only one unique column, use it as the target and update all other columns
        if len(unique_cols) == 1:
            return query.on_conflict(
                target=unique_cols[0],
                action=OnConflictAction.DO_UPDATE,
                values=cls.on_conflict_update_columns(
                    [unique_cols[0]._meta.name]
                ),
            )
        # If there is one unique constraint, use that as the target and update all other columns
        else:
            if len(cls._meta.constraints) == 1:
                chosen_constraint = cls._meta.constraints[0]
                chosen_constraint_cols = cls.on_conflict_update_columns(
                    chosen_constraint._meta.params['unique_columns']
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
    def get_column_by_name(cls, name: str):
        for c in cls._meta.columns:
            if c._meta.name == name:
                return c
        return None

    @classmethod
    # @lru_cache(maxsize=1)
    def on_conflict_update_columns(cls, excluded_names: list[str]):
        excluded_names += ['id', 'created_at', 'updated_at', 'deactivated']
        return [c for c in cls._meta.columns if not c._meta.unique and c._meta.name not in excluded_names]

    @classmethod
    # @lru_cache(maxsize=1)
    def unique_columns(cls):
        excluded_names = ['id', 'created_at', 'updated_at', 'deactivated']
        return [c for c in cls._meta.columns if c._meta.unique and c._meta.name not in excluded_names]

    # TODO: Fix when composite unique constraint functionality is available
    @classmethod
    async def upsert_one(
        cls,
        dto: CreateDTOClassType,
    ) -> ReadDTOClassType:
        item = cls(**dto.model_dump())
        await cls.add_on_conflict_params(cls.insert(item)).run()
        await item.refresh()
        return cls.ReadDTOClass.model_construct(**item.to_dict())

    @classmethod
    @lru_cache(maxsize=1)
    def batch_size(cls) -> int:
        max_batch_size = 10000
        return int(max_batch_size / len(cls._meta.columns))

    @classmethod
    async def create_many(cls, dtos: list[CreateDTOClassType]) -> AppBulkActionResultDTO:
        batch_size = cls.batch_size()
        batch_res = []
        batch_number = 1

        start = time.monotonic()
        for i in range(0, len(dtos), batch_size):
            batch_items = dtos[i:i+batch_size]
            q = cls.insert(
                *[cls(**i.model_dump()) for i in batch_items]
            ).run()
            batch_res.append(await q)
            logger.info(f"Batch {batch_number} size {len(batch_items)}: items idx={i} to idx={i+len(batch_items)-1} inserted.")
            batch_number += 1
        logger.info(f"Time taken: {time.monotonic() - start} seconds.")

        return AppBulkActionResultDTO.model_construct(
            ids=[
                r['id'] for r in [r for batch in batch_res for r in batch]
            ]
        )

    @classmethod
    async def upsert_many(cls, dtos: list[CreateDTOClassType]) -> AppBulkActionResultDTO:
        batch_size = cls.batch_size()
        batch_res = []
        batch_number = 1

        start = time.monotonic()
        for i in range(0, len(dtos), batch_size):
            batch_items = dtos[i:i+batch_size]
            q = cls.add_on_conflict_params(
                cls.insert(
                    *[cls(**i.model_dump()) for i in batch_items]
                )
            ).run()
            batch_res.append(await q)
            logger.info(f"Batch {batch_number} size {len(batch_items)}: items idx={i} to idx={i+len(batch_items)-1} inserted.")
            batch_number += 1
        logger.info(f"Time taken: {time.monotonic() - start} seconds.")

        return AppBulkActionResultDTO.model_construct(
            ids=[
                r['id'] for r in [r for batch in batch_res for r in batch]
            ]
        )

    @classmethod
    async def delete_one(cls, id: int) -> None:
        await cls.delete().where(cls.id == id).run()

    @classmethod
    async def delete_all(cls, force: bool = False) -> AppDeleteAllResponseDTO:
        count = await cls.count().run()
        res = await cls.delete(force=True).run()
        logger.info(f"Deleted {count} items.")
        return AppDeleteAllResponseDTO.model_construct(count=count)
