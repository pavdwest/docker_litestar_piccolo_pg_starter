from src.logging.service import logger

from src.database.service import db
from src.database.models import DatabaseBind
from src.app import create_app
from src.lifespan import lifespan
from src.config import (
    DATABASE_HOST_NAME,
    DATABASE_HOST_PORT,
    DATABASE_HOST_USERNAME,
    DATABASE_HOST_PASSWORD,
    DATABASE_NAME,
)


logger.info("Starting the application...")


# Init db
db.init(
    DatabaseBind(
        host=DATABASE_HOST_NAME,
        name=DATABASE_NAME,
        username=DATABASE_HOST_USERNAME,
        password=DATABASE_HOST_PASSWORD,
        port=DATABASE_HOST_PORT,
    )
)


# Init app
app = create_app(lifespan=[lifespan])
