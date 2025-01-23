import time
from typing import Optional

from piccolo.engine.postgres import PostgresEngine
from sqlalchemy_utils import database_exists, create_database

from src.logging.service import logger
from src.database.exceptions import DatabaseNotFoundException
from src.database.models import DatabaseBind
from src.models.all import MODELS


class DatabaseService:
    RETRY_COUNT_DEFAULT = 10
    RETRY_DELAY_DEFAULT = 1.0

    def __init__(self):
        self.DATABASE: Optional[PostgresEngine] = None
        self.DATABASE_BIND: Optional[DatabaseBind] = None
        self._retry_count: int = self.RETRY_COUNT_DEFAULT
        self._retry_delay: float = self.RETRY_DELAY_DEFAULT

    def init(
        self,
        database_bind: DatabaseBind,
        retry_count: int = RETRY_COUNT_DEFAULT,
        retry_delay: float = RETRY_DELAY_DEFAULT,
        use_pool: bool = True,
    ) -> None:
        """
        Initialize the database service with the given database bind.
        """
        self.DATABASE_BIND = database_bind
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self.use_pool = use_pool

        # Shared DB
        self.create_db(self.DATABASE_BIND, self._retry_count, self._retry_delay)
        self.DATABASE = self.init_engine(self.DATABASE_BIND)
        self.create_tables(self.DATABASE)

    @classmethod
    def create_db(
        cls,
        bind: DatabaseBind,
        retry_count: int = RETRY_COUNT_DEFAULT,
        retry_delay: float = RETRY_DELAY_DEFAULT,
    ) -> None:
        """
        Create a database if it doesn't exist.
        Parameterised to allow future support for multiple databases.
        """
        for _ in range(retry_count):
            try:
                if database_exists(bind.url_sync):
                    logger.info("Database found.")
                    return
                logger.warning("Creating database...")
                create_database(bind.url_sync)
                return
            except Exception as e:
                logger.error(f"Error creating database: {e}")
                last_exception = e
                time.sleep(retry_delay)
        logger.critical(f"Failed to create database after {retry_count} retries.")
        raise DatabaseNotFoundException(bind.name) from last_exception

    @classmethod
    def init_engine(
        self,
        bind: DatabaseBind,
    ) -> None:
        """
        Utility method to initialize a database engine.
        Parameterised to allow future support for multiple databases.
        """
        logger.info("Initialising database engine...")
        return PostgresEngine(
            config=bind.piccolo_config,
            # log_queries=True,
            # log_responses=True,
        )

    @classmethod
    def create_tables(cls, engine: PostgresEngine) -> None:
        """
        Create the database tables.
        """
        logger.info("Creating database tables...")
        models = MODELS.get_all()

        for Model in models:
            Model._meta.db = engine
            Model.create_table(if_not_exists=True).run_sync()

    @classmethod
    async def open_engine_pool(cls, engine: PostgresEngine) -> None:
        await engine.start_connection_pool()

    @classmethod
    async def close_engine_pool(cls, engine: PostgresEngine) -> None:
        if engine.pool:
            await engine.close_connection_pool()

    async def open_connection_pools(self) -> None:
        if self.use_pool:
            await self.open_engine_pool(self.DATABASE)

    async def close_connection_pools(self) -> None:
        if self.use_pool:
            await self.close_engine_pool(self.DATABASE)


db = DatabaseService()
