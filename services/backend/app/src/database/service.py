
from src.logging.service import logger


logger.warning('BEFORE PICCOLO IMPORT')
from piccolo.engine.postgres import PostgresEngine
logger.warning('AFTER PICCOLO IMPORT')


import time

from sqlalchemy_utils import database_exists, create_database

from src.logging.service import logger
from src.database.models import DatabaseBind
from src.base.models.all import get_all_app_models_list
from src.base.lifespan import register_on_startup, register_on_shutdown


class DatabaseService:
    def __init__(self):
        self.DATABASE = None

    def init(
        self,
        shared_database_bind: DatabaseBind,
    ):
        # Binds
        self.DATABASE_BIND = shared_database_bind
        self._create_db()
        self._init_engine()
        register_on_startup(self.start_connections)
        register_on_shutdown(self.close_connections)

    def _create_db(self):
        logger.info("Creating databases...")
        retries = 10
        retry_delay = 1.0

        for i in range(retries):
            if database_exists(self.DATABASE_BIND.url_sync):
                break
            create_database(self.DATABASE_BIND.url_sync)
            time.sleep(retry_delay)

    def _init_engine(self):
        logger.info("Initialising database engines...")
        self.DATABASE = PostgresEngine(
            config=self.DATABASE_BIND.piccolo_config,
            # log_queries=True,
            # log_responses=True,
        )

    def init_models(self):
        logger.info("Initialising models...")
        self._create_tables()

    def _create_tables(self):
        logger.info("Creating database tables...")
        models = get_all_app_models_list()

        for Model in models:
            Model._meta.db = self.DATABASE
            Model.create_table(if_not_exists=True, auto_create_schema=True).run_sync()

    async def start_connections(self):
        logger.info("Starting database engine pools...")
        await self.DATABASE.start_connection_pool()

    async def close_connections(self):
        logger.info("Shutting down database engines...")
        if self.DATABASE.pool:
            await self.DATABASE.close_connection_pool()


db = DatabaseService()
