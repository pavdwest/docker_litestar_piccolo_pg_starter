import time
from typing import Optional

from piccolo.engine.postgres import PostgresEngine
from sqlalchemy_utils import database_exists, create_database

from src.logging.service import logger
from src.database.models import DatabaseBind
from src.database.exceptions import DatabaseNotFoundException
from src.base.models.all import get_all_app_models_list
from src.base.lifespan import register_on_startup, register_on_shutdown


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
        shared_database_bind: DatabaseBind,
        retry_count: int = RETRY_COUNT_DEFAULT,
        retry_delay: float = RETRY_DELAY_DEFAULT,
    ) -> None:
        """
        Initialize the database service with the given database bind.
        """
        self.DATABASE_BIND = shared_database_bind
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._create_db()
        self._init_engine()
        register_on_startup(self.start_connections)
        register_on_shutdown(self.close_connections)

    def _create_db(self) -> None:
        """
        Create the database if it does not exist.
        """
        for _ in range(self._retry_count):
            try:
                if database_exists(self.DATABASE_BIND.url_sync):
                    logger.info("Database found.")
                    return
                logger.warning("Creating database...")
                create_database(self.DATABASE_BIND.url_sync)
                return
            except Exception as e:
                logger.error(f"Error creating database: {e}")
                last_exception = e
                time.sleep(self._retry_delay)
        logger.critical(f"Failed to create database after {self._retry_count} retries.")
        raise DatabaseNotFoundException(self.DATABASE_BIND.name) from last_exception

    def _init_engine(self) -> None:
        """
        Initialize the database engine.
        """
        logger.info("Initializing database engines...")
        self.DATABASE = PostgresEngine(
            config=self.DATABASE_BIND.piccolo_config,
            # log_queries=True,
            # log_responses=True,
        )

    def init_models(self) -> None:
        """
        Initialize the database models.
        """
        logger.info("Initializing models...")
        self._create_tables()

    def _create_tables(self) -> None:
        """
        Create the database tables.
        """
        logger.info("Creating database tables...")
        models = get_all_app_models_list()

        for Model in models:
            Model._meta.db = self.DATABASE
            Model.create_table(if_not_exists=True, auto_create_schema=True).run_sync()

    async def start_connections(self) -> None:
        """
        Start the database connection pools.
        """
        logger.info("Starting database engine pools...")
        await self.DATABASE.start_connection_pool()

    async def close_connections(self) -> None:
        """
        Close the database connection pools.
        """
        logger.info("Shutting down database engines...")
        if self.DATABASE.pool:
            await self.DATABASE.close_connection_pool()


db = DatabaseService()
