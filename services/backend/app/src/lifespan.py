from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import Litestar

from src.logging.service import logger
from src.database.service import db


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Startup...")
    await db.open_connection_pools()
    yield
    # Shutdown
    logger.info("Shutdown...")
    await db.close_connection_pools()
